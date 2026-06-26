import pytest

from app.auth import otp

FIXED = "123456"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _register(client, **kw):
    r = client.post("/auth/register", json=kw)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _verify(client, dinh_danh):
    r = client.post("/auth/verify-otp", json={"dinh_danh": dinh_danh, "ma": FIXED})
    assert r.status_code == 200, r.text


def _login(client, dinh_danh, password):
    return client.post("/auth/login", json={"dinh_danh": dinh_danh, "password": password})


def test_dang_ky_xac_thuc_dang_nhap(client):
    _register(client, email="hs@x.com", password="matkhau123")
    # Chưa xác thực OTP → login bị chặn
    assert _login(client, "hs@x.com", "matkhau123").status_code == 403
    _verify(client, "hs@x.com")
    r = _login(client, "hs@x.com", "matkhau123")
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_otp_sai_khong_kich_hoat(client):
    _register(client, email="hs2@x.com", password="matkhau123")
    r = client.post("/auth/verify-otp", json={"dinh_danh": "hs2@x.com", "ma": "000000"})
    assert r.status_code == 400


def test_vi_thanh_nien_can_dong_y(client):
    child_id = _register(client, email="con@x.com", password="matkhau123", la_vi_thanh_nien=True)
    _verify(client, "con@x.com")
    # Vị thành niên chưa có đồng ý phụ huynh → 403 (FR-C03)
    assert _login(client, "con@x.com", "matkhau123").status_code == 403

    _register(client, email="ph@x.com", password="matkhau123", vai_tro="phu_huynh")
    _verify(client, "ph@x.com")
    ph_token = _login(client, "ph@x.com", "matkhau123").json()["access_token"]
    r = client.post(
        "/auth/parent-consent",
        json={"child_id": child_id},
        headers={"Authorization": f"Bearer {ph_token}"},
    )
    assert r.status_code == 200, r.text
    # Sau khi có đồng ý → đăng nhập được
    assert _login(client, "con@x.com", "matkhau123").status_code == 200


def test_rbac_admin_only(client):
    _register(client, email="hs3@x.com", password="matkhau123")
    _verify(client, "hs3@x.com")
    hs_token = _login(client, "hs3@x.com", "matkhau123").json()["access_token"]
    # Học sinh KHÔNG vào được route quản trị
    r = client.get("/auth/admin-only", headers={"Authorization": f"Bearer {hs_token}"})
    assert r.status_code == 403

    _register(client, email="ad@x.com", password="matkhau123", vai_tro="quan_tri")
    _verify(client, "ad@x.com")
    ad_token = _login(client, "ad@x.com", "matkhau123").json()["access_token"]
    r = client.get("/auth/admin-only", headers={"Authorization": f"Bearer {ad_token}"})
    assert r.status_code == 200

    # Không có token → bị chặn
    assert client.get("/auth/admin-only").status_code in (401, 403)
