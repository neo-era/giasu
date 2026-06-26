import pytest

from app.auth import otp
from app.models.enums import PhanKhuc
from app.personas import PersonaLoader
from app.router import PERSONA_GIAO_SU_NGO, LLMRouter, RoutingRequest

FIXED = "123456"


def test_router_tinh_hoa_chon_giao_su_ngo():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.tinh_hoa))
    assert d.persona == PERSONA_GIAO_SU_NGO
    assert d.bac.value == "reasoning"


def test_prompt_giao_su_ngo_khong_giai_ho():
    tpl = PersonaLoader().load("giao_su_ngo")
    assert "KHÔNG GIẢI HỘ" in tpl.text
    assert tpl.required_vars == set()  # không cần biến


# ---- End-to-end: tinh hoa dùng bậc reasoning, đại trà dùng bậc rẻ ----
@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email, phan_khuc=None):
    body = {"email": email, "password": "matkhau123"}
    if phan_khuc:
        body["phan_khuc"] = phan_khuc
    client.post("/auth/register", json=body)
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {tok}"}


def _gui(client, h, noi_dung="Phân tích bài này"):
    cid = client.post("/chat/conversations", json={}, headers=h).json()["id"]
    return client.post(
        f"/chat/conversations/{cid}/messages", json={"noi_dung": noi_dung}, headers=h
    ).json()


def test_tinh_hoa_dung_bac_reasoning(client):
    h = _auth(client, "elite@x.com", phan_khuc="tinh_hoa")
    msg = _gui(client, h)
    assert msg["model_dung"] == "mock-reasoning"  # bậc reasoning cho tinh hoa


def test_dai_tra_free_dung_bac_re(client):
    h = _auth(client, "mass@x.com")  # mặc định đại trà, gói free
    msg = _gui(client, h)
    assert msg["model_dung"] == "mock-fast"  # bậc rẻ cho đại trà free
