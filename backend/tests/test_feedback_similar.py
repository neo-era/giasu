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


def test_goi_y_phan_anh_tuong_tu(client):
    h = _auth(client)
    client.post(
        "/feedback",
        json={
            "chu_de": "loi_loi_giai",
            "tieu_de": "Bài tích phân sai",
            "noi_dung": "Bước hai nhầm dấu",
        },
        headers=h,
    )
    client.post(
        "/feedback",
        json={"chu_de": "gop_y", "tieu_de": "Giao diện tối", "noi_dung": "Nên có chế độ sáng"},
        headers=h,
    )
    # Gửi truy vấn gần với phản ánh thứ nhất → nó phải đứng đầu
    r = client.get("/feedback/tuong-tu", params={"q": "bài tích phân nhầm dấu"}, headers=h)
    assert r.status_code == 200
    items = r.json()
    assert items
    assert "tích phân" in items[0]["tieu_de"].lower()
