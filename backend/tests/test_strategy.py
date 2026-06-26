import pytest

from app.auth import otp
from app.llm import ChatResult, LLMService, registry
from app.llm.base import LLMProvider
from app.strategy.service import sinh_cay

FIXED = "123456"

TREE_JSON = (
    '{"ban_chat":"Dùng bất biến.","huong_tiep_can":['
    '{"ten":"Đại số","y_tuong":"xét đa thức đặc trưng","khi_nao_phu_hop":"khi đối xứng",'
    '"do_kho_tuong_doi":"kho"},'
    '{"ten":"Tổ hợp","y_tuong":"đếm hai cách","khi_nao_phu_hop":"rời rạc",'
    '"do_kho_tuong_doi":"vua"}]}'
)


class _Scripted(LLMProvider):
    name = "scripted"

    def __init__(self, text: str) -> None:
        self.text = text

    def chat(self, messages, model, **kw) -> ChatResult:
        return ChatResult(text=self.text, model=model, provider=self.name)


def test_sinh_cay_2_huong_khong_lo_loi_giai():
    registry.reset_registry()
    registry.register_provider(_Scripted(TREE_JSON))
    tree = sinh_cay("đề khó", LLMService(tiers={"reasoning": "scripted:m"}, backoff=0))
    assert len(tree.huong_tiep_can) == 2
    # Không có trường lời giải trong cấu trúc trả về
    assert "loi_giai" not in tree.model_dump()
    registry.reset_registry()


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email="elite@x.com"):
    client.post(
        "/auth/register", json={"email": email, "password": "matkhau123", "phan_khuc": "tinh_hoa"}
    )
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def test_api_tree_va_chon_huong(client):
    h = _auth(client)
    r = client.post("/strategy/tree", json={"de_latex": "$a^n+b^n$"}, headers=h)
    assert r.status_code == 200
    assert "huong_tiep_can" in r.json()

    # Gửi tin nhắn kèm hướng đã chọn → tiếp tục đúng nhánh (200)
    cid = client.post("/chat/conversations", json={}, headers=h).json()["id"]
    r2 = client.post(
        f"/chat/conversations/{cid}/messages",
        json={"noi_dung": "Em thử hướng này", "huong_tiep_can": "Đại số"},
        headers=h,
    )
    assert r2.status_code == 200
