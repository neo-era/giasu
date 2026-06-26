import pytest

from app.auth import otp

FIXED = "123456"


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


def _tao_phan_anh(client, h) -> str:
    return client.post(
        "/feedback",
        json={"chu_de": "loi_loi_giai", "tieu_de": "Bài 5", "noi_dung": "Sai bước 3"},
        headers=h,
    ).json()["id"]


def test_hs_khong_duoc_tra_loi_hay_doi_trang_thai(client):
    hs = _auth(client, "hs@x.com")
    pid = _tao_phan_anh(client, hs)
    assert (
        client.post(f"/feedback/{pid}/reply", json={"noi_dung": "x"}, headers=hs).status_code == 403
    )
    assert (
        client.patch(
            f"/feedback/{pid}/status", json={"trang_thai": "da_dong"}, headers=hs
        ).status_code
        == 403
    )


def test_doi_ngu_tra_loi_tu_chuyen_trang_thai(client):
    hs = _auth(client, "hs2@x.com")
    team = _auth(client, "bt@x.com", vai_tro="bien_tap")
    pid = _tao_phan_anh(client, hs)

    r = client.post(f"/feedback/{pid}/reply", json={"noi_dung": "Đội ngũ đã sửa."}, headers=team)
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "da_tra_loi"  # tự chuyển trạng thái

    comments = client.get(f"/feedback/{pid}/comments", headers=hs).json()
    assert any(c["la_phan_hoi_chinh_thuc"] for c in comments)


def test_doi_ngu_doi_trang_thai(client):
    team = _auth(client, "bt2@x.com", vai_tro="bien_tap")
    pid = _tao_phan_anh(client, team)
    r = client.patch(f"/feedback/{pid}/status", json={"trang_thai": "dang_xu_ly"}, headers=team)
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "dang_xu_ly"
