import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.models.enums import TrangThaiKiemDuyet
from app.moderation.pii import che_thong_tin_ca_nhan
from app.moderation.service import ModerationResult, classify_text

FIXED = "123456"


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


# ---- PII: che tất định ----
def test_che_email_va_sdt():
    text, found = che_thong_tin_ca_nhan("Liên hệ a@b.com hoặc 0912345678 nhé")
    assert found is True
    assert "a@b.com" not in text
    assert "0912345678" not in text
    assert "[đã ẩn]" in text


def test_khong_co_pii():
    text, found = che_thong_tin_ca_nhan("Bài 3 sai ở bước 2")
    assert found is False
    assert text == "Bài 3 sai ở bước 2"


# ---- Phân loại P9 ----
def test_classify_chan():
    registry.reset_registry()
    registry.register_provider(_Scripted('{"quyet_dinh":"chan","vi_pham":["ngon_tu_doc_hai"]}'))
    r = classify_text("xxx", LLMService(tiers={"re": "scripted:m"}, backoff=0))
    assert r.quyet_dinh == TrangThaiKiemDuyet.chan
    registry.reset_registry()


def test_classify_fallback_cho_phep():
    registry.reset_registry()
    from app.llm.providers.mock import MockProvider

    registry.register_provider(MockProvider())
    r = classify_text("nội dung lành mạnh", LLMService(tiers={"re": "mock:m"}, backoff=0))
    assert r.quyet_dinh == TrangThaiKiemDuyet.cho_phep
    registry.reset_registry()


# ---- API: nội dung độc hại bị chặn (không hiển thị) ----
@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email="hs@x.com"):
    client.post("/auth/register", json={"email": email, "password": "matkhau123"})
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_noi_dung_doc_hai_bi_chan(client, monkeypatch):
    # Ép moderation trả 'chặn' cho nội dung này
    monkeypatch.setattr(
        "app.feedback.service.classify_text",
        lambda text, llm=None: ModerationResult(quyet_dinh=TrangThaiKiemDuyet.chan),
    )
    h = _auth(client)
    r = client.post(
        "/feedback",
        json={"chu_de": "khac", "tieu_de": "spam", "noi_dung": "nội dung xấu"},
        headers=h,
    )
    assert r.status_code == 201
    assert r.json()["trang_thai_kiem_duyet"] == "chan"
    # Không xuất hiện trong danh sách công khai
    items = client.get("/feedback", headers=h).json()
    assert all(i["id"] != r.json()["id"] for i in items)


def test_lo_sdt_bi_che_khi_dang(client):
    h = _auth(client, "pii@x.com")
    r = client.post(
        "/feedback",
        json={"chu_de": "khac", "tieu_de": "Hỏi", "noi_dung": "Gọi tôi 0987654321"},
        headers=h,
    )
    assert r.status_code == 201
    assert "0987654321" not in r.json()["noi_dung"]
    assert "[đã ẩn]" in r.json()["noi_dung"]
