import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockProvider
from app.ocr.service import OcrService

FIXED = "123456"

JSON_RO = (
    '{"de_latex":"$x^2=4$","mon":"toan","lop":12,'
    '"phan_khuc_goi_y":"dai_tra","do_kho":"thong_hieu",'
    '"ocr_tin_cay":0.95,"can_xac_nhan_lai":false}'
)
JSON_MO = (
    'Đây là kết quả: {"de_latex":"$x^?=?$","mon":"toan","lop":null,'
    '"phan_khuc_goi_y":"dai_tra","do_kho":"thong_hieu",'
    '"ocr_tin_cay":0.2,"can_xac_nhan_lai":false}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def _svc(text: str) -> OcrService:
    registry.reset_registry()
    registry.register_provider(_Scripted(text))
    llm = LLMService(tiers={"vision": "scripted:m"}, backoff=0)
    return OcrService(llm=llm)


def test_anh_ro_khong_can_xac_nhan():
    r = _svc(JSON_RO).extract(text="x^2=4")
    assert r.can_xac_nhan_lai is False
    assert r.de_latex == "$x^2=4$"
    assert r.ocr_tin_cay == 0.95


def test_anh_mo_buoc_xac_nhan():
    # Model trả can_xac_nhan_lai=false nhưng tin cậy 0.2 < ngưỡng → vẫn buộc
    r = _svc(JSON_MO).extract(text="mờ")
    assert r.ocr_tin_cay == 0.2
    assert r.can_xac_nhan_lai is True


def test_khong_phai_json_thi_fallback_an_toan():
    registry.reset_registry()
    registry.register_provider(MockProvider())
    svc = OcrService(llm=LLMService(tiers={"vision": "mock:m"}, backoff=0))
    r = svc.extract(text="2x+1")
    assert r.ocr_tin_cay == 0.0
    assert r.can_xac_nhan_lai is True
    registry.reset_registry()


# ---- API: chặn xử lý khi chưa xác nhận ----


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


def test_confirm_chan_khi_chua_xac_nhan(client):
    h = _auth(client)
    r = client.post(
        "/ocr/confirm",
        json={"de_latex": "$x=1$", "can_xac_nhan_lai": True, "da_xac_nhan": False},
        headers=h,
    )
    assert r.status_code == 409


def test_confirm_tao_de_khi_da_xac_nhan(client):
    h = _auth(client)
    r = client.post(
        "/ocr/confirm",
        json={
            "de_latex": "$x=1$",
            "mon": "toan",
            "lop": 12,
            "can_xac_nhan_lai": True,
            "da_xac_nhan": True,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert r.json()["de_latex"] == "$x=1$"
