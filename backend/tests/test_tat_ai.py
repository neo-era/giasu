import pytest

from app.auth import otp
from app.tat_ai.service import hieu_chinh_do_kho

FIXED = "123456"


def test_hieu_chinh_do_kho():
    assert hieu_chinh_do_kho(9.0) == "tang"  # quá dễ
    assert hieu_chinh_do_kho(3.0) == "giam"  # quá khó
    assert hieu_chinh_do_kho(6.0) == "giu"  # vùng vật lộn hiệu quả


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


def test_ghi_ket_qua_cap_nhat_bang_tu_giai(client):
    h = _auth(client)
    r = client.post("/tat-ai/ket-qua", json={"diem": 9.0}, headers=h)
    assert r.status_code == 201
    assert r.json()["hieu_chinh_do_kho"] == "tang"

    client.post("/tat-ai/ket-qua", json={"diem": 5.0}, headers=h)
    bang = client.get("/tat-ai/bang", headers=h).json()
    # Tỷ lệ tự giải cập nhật (2 lần đo), KHÔNG có chỉ số engagement
    assert bang["ty_le_tu_giai"] == [9.0, 5.0]
    assert "engagement" not in bang
