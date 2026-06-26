import pytest

from app.auth import otp

FIXED = "123456"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def _auth(client, email, vai_tro=None, la_vi_thanh_nien=False):
    body = {"email": email, "password": "matkhau123", "la_vi_thanh_nien": la_vi_thanh_nien}
    if vai_tro:
        body["vai_tro"] = vai_tro
    rid = client.post("/auth/register", json=body).json()["id"]
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()
    headers = {"Authorization": f"Bearer {tok['access_token']}"} if "access_token" in tok else {}
    return rid, headers


def test_phu_huynh_xem_bao_cao_con(client):
    child_id, _ = _auth(client, "con@x.com", la_vi_thanh_nien=True)
    _, ph = _auth(client, "ph@x.com", vai_tro="phu_huynh")
    # Liên kết + đồng ý
    client.post("/auth/parent-consent", json={"child_id": child_id}, headers=ph)

    con = client.get("/phu-huynh/con-cua-toi", headers=ph).json()
    assert any(c["id"] == child_id for c in con)

    r = client.get(f"/phu-huynh/con/{child_id}/bao-cao", headers=ph)
    assert r.status_code == 200
    assert "ty_le_tu_giai" in r.json()
    assert "khai_niem_hay_sai" in r.json()


def test_khong_xem_con_nguoi_khac(client):
    child_id, _ = _auth(client, "con2@x.com", la_vi_thanh_nien=True)
    _, ph_khac = _auth(client, "ph2@x.com", vai_tro="phu_huynh")
    # Phụ huynh chưa liên kết với child_id → 403
    r = client.get(f"/phu-huynh/con/{child_id}/bao-cao", headers=ph_khac)
    assert r.status_code == 403
