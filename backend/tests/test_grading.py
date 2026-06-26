import pytest

from app.auth import otp
from app.grading.service import cham
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider

FIXED = "123456"

# Bước 1 đúng (0.5đ) nhưng đáp số cuối sai (bước 2 sai, 0đ) → vẫn được điểm thành phần
JSON_PARTIAL = (
    '{"cac_buoc":['
    '{"noi_dung":"Đặt ẩn đúng","dung":true,"diem_thanh_phan":0.5,"nhan_xet":""},'
    '{"noi_dung":"Tính sai dấu","dung":false,"diem_thanh_phan":0,"nhan_xet":"nhầm dấu"}'
    '],"tong_diem_uoc_luong":0.5,"loi_pho_bien_mac_phai":["nhầm dấu"],'
    '"goi_y_trinh_bay_de_an_diem":"ghi rõ từng bước"}'
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
    return LLMService(tiers={"can_bang": "scripted:m"}, backoff=0)


def test_cong_nhan_diem_thanh_phan_du_dap_so_sai():
    r = cham("bài làm", "mẫu", "barem", llm=_svc(JSON_PARTIAL))
    assert r.tong_diem_uoc_luong == 0.5  # vẫn có điểm dù đáp số cuối sai
    assert r.cac_buoc[0].dung is True
    registry.reset_registry()


def test_khong_cham_khat_khe_hon_barem_clamp():
    # Model lỡ trả điểm vượt barem → bị kẹp về điểm tối đa
    over = JSON_PARTIAL.replace('"tong_diem_uoc_luong":0.5', '"tong_diem_uoc_luong":99')
    r = cham("x", "y", "z", diem_toi_da=1.0, llm=_svc(over))
    assert r.tong_diem_uoc_luong == 1.0
    registry.reset_registry()


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def test_api_grade_khong_lo_loi_giai_mau(client):
    email = "hs@x.com"
    client.post("/auth/register", json={"email": email, "password": "matkhau123"})
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    r = client.post(
        "/grade",
        json={"bai_lam": "a", "loi_giai_mau": "BÍ MẬT", "barem": "b"},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    # Phản hồi KHÔNG chứa lời giải mẫu
    assert "loi_giai_mau" not in r.json()
