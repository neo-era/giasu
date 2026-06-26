import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.proof.service import critique, tinh_chi_so

FIXED = "123456"

JSON_LO_HONG = (
    '{"cac_buoc":[{"buoc":"Dùng BĐT Cauchy","trang_thai":"sai",'
    '"ly_do":"thiếu điều kiện dương"}],"edge_cases_bo_sot":["x=0"],'
    '"ket_luan_so_bo":"co_lo_hong","do_tin_cay":0.7,"can_nguoi_duyet":true}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def test_critique_phat_hien_lo_hong():
    registry.reset_registry()
    registry.register_provider(_Scripted(JSON_LO_HONG))
    r = critique("CM ...", LLMService(tiers={"reasoning": "scripted:m"}, backoff=0))
    assert r.ket_luan_so_bo == "co_lo_hong"
    assert r.phat_hien_lo_hong is True
    assert r.can_nguoi_duyet is True
    registry.reset_registry()


def test_critique_fallback_khong_du_can_cu():
    from app.llm.providers.mock import MockProvider

    registry.reset_registry()
    registry.register_provider(MockProvider())
    r = critique("CM ...", LLMService(tiers={"reasoning": "mock:m"}, backoff=0))
    # Không parse được → trung thực: không đủ căn cứ + cần người duyệt
    assert r.ket_luan_so_bo == "khong_du_can_cu"
    assert r.can_nguoi_duyet is True
    registry.reset_registry()


def test_tinh_chi_so_detection_va_false_rates():
    # 4 CM: 2 có lỗi, 2 đúng. Phát hiện 1/2 lỗi; báo nhầm 1/2 đúng.
    ket_qua = [
        (True, True),  # đúng phát hiện
        (False, True),  # bỏ sót (false negative)
        (True, False),  # báo nhầm (false positive)
        (False, False),  # đúng (không lỗi)
    ]
    cs = tinh_chi_so(ket_qua)
    assert cs["detection_rate"] == 0.5
    assert cs["false_positive_rate"] == 0.5
    assert cs["false_negative_rate"] == 0.5


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def test_api_critique(client):
    email = "elite@x.com"
    client.post(
        "/auth/register",
        json={"email": email, "password": "matkhau123", "phan_khuc": "tinh_hoa"},
    )
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    r = client.post(
        "/proof/critique",
        json={"chung_minh": "Giả sử ..."},
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    assert "ket_luan_so_bo" in r.json()
