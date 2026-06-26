import pytest

from app.auth import otp

FIXED = "123456"


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


def test_tao_va_doc_phan_anh(client):
    h = _auth(client)
    r = client.post(
        "/feedback",
        json={"chu_de": "gop_y", "tieu_de": "Giao diện", "noi_dung": "Nên to chữ hơn"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    assert r.json()["trang_thai"] == "moi"

    items = client.get("/feedback", headers=h).json()
    assert any(i["tieu_de"] == "Giao diện" for i in items)


def test_an_danh_khong_lo_danh_tinh(client):
    h = _auth(client, "an@x.com")
    r = client.post(
        "/feedback",
        json={
            "chu_de": "loi_loi_giai",
            "tieu_de": "Bài 3 sai",
            "noi_dung": "Bước 2 nhầm dấu",
            "an_danh": True,
        },
        headers=h,
    )
    assert r.status_code == 201
    assert r.json()["an_danh"] is True
    assert r.json()["nguoi_gui_id"] is None  # ẩn danh → không lộ người gửi


def test_loc_theo_chu_de(client):
    h = _auth(client)
    client.post(
        "/feedback",
        json={"chu_de": "thanh_toan", "tieu_de": "Lỗi QR", "noi_dung": "Không quét được"},
        headers=h,
    )
    items = client.get("/feedback?chu_de=thanh_toan", headers=h).json()
    assert items
    assert all(i["chu_de"] == "thanh_toan" for i in items)
