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


def _tao_loi(client, h) -> str:
    return client.post(
        "/feedback",
        json={"chu_de": "loi_loi_giai", "tieu_de": "Bài 7 sai", "noi_dung": "Bước 4 nhầm"},
        headers=h,
    ).json()["id"]


def test_dong_tinh_chi_mot_lan(client):
    a = _auth(client, "a@x.com")
    pid = _tao_loi(client, a)
    assert client.post(f"/feedback/{pid}/dong-tinh", headers=a).json()["so_dong_tinh"] == 1
    # Đồng tình lần 2 cùng người → không tăng
    assert client.post(f"/feedback/{pid}/dong-tinh", headers=a).json()["so_dong_tinh"] == 1


def test_binh_luan_cong_dong(client):
    a = _auth(client, "b@x.com")
    pid = _tao_loi(client, a)
    r = client.post(f"/feedback/{pid}/comment", json={"noi_dung": "Mình cũng thấy vậy"}, headers=a)
    assert r.status_code == 201


def test_uc04_phan_anh_loi_den_kiem_chung_va_hoi_quy(client):
    student = _auth(client, "hs@x.com")
    hlv = _auth(client, "hlv@x.com", vai_tro="hlv")
    pid = _tao_loi(client, student)

    # F09: phản ánh lỗi đã được đẩy vào hàng đợi rà soát (HITL)
    q = client.get("/review/queue", headers=hlv).json()
    assert any(i["loai"] == "phan_anh_loi" for i in q)

    # Đội ngũ giải quyết → cập nhật trạng thái + bộ hồi quy + thông báo
    r = client.post(
        f"/feedback/{pid}/giai-quyet-loi",
        json={"mo_ta_sua": "Sửa bước 4, thêm ca hồi quy"},
        headers=hlv,
    )
    assert r.status_code == 200
    assert r.json()["trang_thai"] == "da_tra_loi"

    # F10: người gửi nhận được thông báo
    tb = client.get("/feedback/thong-bao/cua-toi", headers=student).json()
    assert tb and "đã được xử lý" in tb[0]["noi_dung"]
