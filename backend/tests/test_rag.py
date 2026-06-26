import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockProvider
from app.rag.service import doi_chieu, ingest, truy_hoi

FIXED = "123456"

JSON_KHOP = (
    '{"khop_voi_nguon":"khop","diem_khac_biet":[],'
    '"trich_dan":[{"y":"định lý X","nguon":"Kỷ yếu IMO 2019"}],'
    '"do_tin_cay":0.8,"can_nguoi_duyet":false}'
)


class _ScriptedWithEmbed(LLMProvider):
    """Có chat theo kịch bản + embed của mock (để truy hồi hoạt động)."""

    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text
        self._mock = MockProvider()

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)

    def embed(self, texts, model):
        return self._mock.embed(texts, model)


def _svc(text: str) -> LLMService:
    registry.reset_registry()
    registry.register_provider(_ScriptedWithEmbed(text))
    return LLMService(tiers={"re": "scripted:m", "reasoning": "scripted:m"}, backoff=0)


def test_ingest_va_truy_hoi(session):
    svc = _svc(JSON_KHOP)
    ingest(session, "Nguồn A", "định lý về số nguyên tố", svc)
    ingest(session, "Nguồn B", "hình học phẳng tam giác", svc)
    ket_qua = truy_hoi(session, "số nguyên tố", k=2, llm=svc)
    assert len(ket_qua) == 2
    registry.reset_registry()


def test_doi_chieu_co_trich_dan(session):
    svc = _svc(JSON_KHOP)
    ingest(session, "Kỷ yếu IMO 2019", "nội dung định lý X", svc)
    r = doi_chieu(session, "lời giải dùng định lý X", "định lý X", llm=svc)
    assert r.khop_voi_nguon == "khop"
    assert r.trich_dan and r.trich_dan[0]["nguon"] == "Kỷ yếu IMO 2019"
    registry.reset_registry()


def test_kho_rong_thi_khong_du_can_cu(session):
    svc = _svc(JSON_KHOP)
    # Chưa nạp tài liệu nào → không đủ căn cứ, chuyển người duyệt (không bịa)
    r = doi_chieu(session, "lời giải", "truy vấn", llm=svc)
    assert r.khop_voi_nguon == "khong_du_can_cu"
    assert r.can_nguoi_duyet is True
    registry.reset_registry()


# ---- API ----
@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email, vai_tro=None):
    body = {"email": email, "password": "matkhau123"}
    if vai_tro:
        body["vai_tro"] = vai_tro
    client.post("/auth/register", json=body)
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_ingest_chi_bien_tap(client):
    hs = _auth(client, "hs@x.com")
    r = client.post("/rag/ingest", json={"nguon": "A", "noi_dung": "x"}, headers=hs)
    assert r.status_code == 403
