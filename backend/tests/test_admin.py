import pytest

from app import runtime_config
from app.auth import otp
from app.config import settings
from app.llm.service import get_llm_service

FIXED = "123456"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


@pytest.fixture(autouse=True)
def restore_runtime():
    yield
    runtime_config.set_tiers(dict(settings.llm_tiers))
    get_llm_service.cache_clear()


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


def test_chi_quan_tri_truy_cap(client):
    hs = _auth(client, "hs@x.com")
    assert client.get("/admin/users", headers=hs).status_code == 403


def test_doi_cau_hinh_router_runtime(client):
    admin = _auth(client, "ad@x.com", vai_tro="quan_tri")
    new = {
        "re": "mock:re-moi",
        "can_bang": "mock:cb-moi",
        "reasoning": "mock:opus-moi",
        "vision": "mock:vision-moi",
    }
    r = client.put("/admin/config/router", json={"tiers": new}, headers=admin)
    assert r.status_code == 200
    assert r.json()["tiers"]["reasoning"] == "mock:opus-moi"
    # Áp dụng runtime: service phân giải model mới mà không deploy lại
    assert get_llm_service().resolve("reasoning")[1] == "opus-moi"


def test_reload_prompt(client):
    admin = _auth(client, "ad2@x.com", vai_tro="quan_tri")
    assert client.post("/admin/config/prompts/reload", headers=admin).status_code == 200


def test_quan_ly_user(client):
    admin = _auth(client, "ad3@x.com", vai_tro="quan_tri")
    hs = _auth(client, "hsx@x.com")  # noqa: F841 — tạo để có trong danh sách
    users = client.get("/admin/users", headers=admin).json()
    target = next(u for u in users if u["email"] == "hsx@x.com")
    r = client.patch(f"/admin/users/{target['id']}", json={"trang_thai": "khoa"}, headers=admin)
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "khoa"
