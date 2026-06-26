import pytest

from app.auth import otp
from app.crosscheck.service import chay_cross_check, so_sanh
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider

FIXED = "123456"

JSON_BAT_DONG = (
    '{"dap_so_khop":false,"diem_bat_dong":["đáp số khác"],'
    '"danh_gia":"bat_dong_can_ra_soat","khuyen_nghi":"chuyen_nguoi_duyet"}'
)
JSON_THONG_NHAT = (
    '{"dap_so_khop":true,"diem_bat_dong":[],"danh_gia":"thong_nhat",' '"khuyen_nghi":"tra_loi"}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def _svc(text: str) -> LLMService:
    registry.reset_registry()
    registry.register_provider(_Scripted(text))
    return LLMService(tiers={"reasoning": "scripted:m"}, backoff=0)


def test_bat_dong_chuyen_nguoi():
    cmp = so_sanh("A", "B", _svc(JSON_BAT_DONG))
    assert cmp.danh_gia == "bat_dong_can_ra_soat"
    assert cmp.can_nguoi_duyet is True
    registry.reset_registry()


def test_thong_nhat_tra_loi():
    cmp = so_sanh("A", "B", _svc(JSON_THONG_NHAT))
    assert cmp.can_nguoi_duyet is False
    registry.reset_registry()


def test_chay_cross_check_tao_hang_doi(session):
    svc = _svc(JSON_BAT_DONG)
    cmp, review_id = chay_cross_check(session, "Chứng minh ...", svc)
    assert cmp.can_nguoi_duyet is True
    assert review_id is not None  # đã tạo mục chờ duyệt
    registry.reset_registry()


def test_fallback_khong_parse_chuyen_nguoi(session):
    from app.llm.providers.mock import MockProvider

    registry.reset_registry()
    registry.register_provider(MockProvider())
    svc = LLMService(tiers={"reasoning": "mock:m"}, backoff=0)
    cmp, review_id = chay_cross_check(session, "bài", svc)
    # Không so khớp được → an toàn: chuyển người duyệt
    assert cmp.can_nguoi_duyet is True
    assert review_id is not None
    registry.reset_registry()


# ---- API: HITL queue + resolve ----
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


def test_hs_khong_xem_duoc_hang_doi(client):
    hs = _auth(client, "hs@x.com")
    assert client.get("/review/queue", headers=hs).status_code == 403


def test_hlv_duyet_doi_ket_luan(client):
    # Tạo mục chờ duyệt qua cross-check (mock → chuyển người)
    student = _auth(client, "elite@x.com")
    cc = client.post("/crosscheck", json={"cau_hoi": "bài khó"}, headers=student).json()
    assert cc["review_id"]

    hlv = _auth(client, "hlv@x.com", vai_tro="hlv")
    q = client.get("/review/queue", headers=hlv).json()
    assert any(i["id"] == cc["review_id"] for i in q)

    r = client.post(
        f"/review/{cc['review_id']}/resolve",
        json={"ket_luan": "Lời giải A đúng, B sai ở bước 3"},
        headers=hlv,
    )
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "da_duyet"
