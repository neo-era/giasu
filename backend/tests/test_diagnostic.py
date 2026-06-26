import pytest

from app.auth import otp
from app.diagnostic.schemas import DiagnosticAnswer, DiagnosticIn
from app.diagnostic.service import DiagnosticService
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockProvider
from app.models.enums import MucDoHoc

FIXED = "123456"

JSON_YEU = (
    '{"level":"yeu","diem_manh":["số học"],"diem_yeu":["phân tích đa thức"],'
    '"khai_niem_can_on_truoc":["hằng đẳng thức"],"do_tin_cay":0.8,'
    '"ghi_chu_cho_giao_vien":""}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def _data() -> DiagnosticIn:
    return DiagnosticIn(
        mon="toan",
        lop=12,
        ket_qua=[DiagnosticAnswer(cau_hoi="2x=4?", dap_an_hs="x=2", dung=True)],
    )


def test_phan_loai_level():
    registry.reset_registry()
    registry.register_provider(_Scripted(JSON_YEU))
    svc = DiagnosticService(LLMService(tiers={"can_bang": "scripted:m"}, backoff=0))
    r = svc.assess(_data())
    assert r.level == MucDoHoc.yeu
    assert "phân tích đa thức" in r.diem_yeu
    registry.reset_registry()


def test_khong_phan_loai_duoc_thi_trung_binh():
    registry.reset_registry()
    registry.register_provider(MockProvider())  # trả text không phải JSON
    svc = DiagnosticService(LLMService(tiers={"can_bang": "mock:m"}, backoff=0))
    r = svc.assess(_data())
    assert r.level == MucDoHoc.trung_binh
    assert r.do_tin_cay == 0.0
    registry.reset_registry()


# ---- API: cập nhật hồ sơ ----


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def test_assess_cap_nhat_ho_so(client):
    email = "hs@x.com"
    client.post("/auth/register", json={"email": email, "password": "matkhau123"})
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    h = {"Authorization": f"Bearer {tok}"}

    r = client.post(
        "/diagnostic/assess",
        json={"mon": "toan", "ket_qua": [{"cau_hoi": "a", "dap_an_hs": "b", "dung": False}]},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["level"] in {"yeu", "trung_binh", "kha_gioi"}
