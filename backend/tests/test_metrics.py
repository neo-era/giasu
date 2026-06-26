import pytest

from app.auth import otp
from app.metrics.service import dashboard, ghi_do, learning_gain
from app.models import NguoiDung
from app.models.enums import GiaiDoanDo, NhomThuNghiem, TrangThaiNguoiDung, VaiTro

FIXED = "123456"


def _user(session, email="hs@x.com") -> NguoiDung:
    u = NguoiDung(email=email, vai_tro=VaiTro.hoc_sinh, trang_thai=TrangThaiNguoiDung.hoat_dong)
    session.add(u)
    session.commit()
    return u


def test_learning_gain_tinh_dung(session):
    app_u = _user(session, "app@x.com")
    ctrl_u = _user(session, "ctrl@x.com")
    # Nhóm app: pre 5 → post 8 (gain 3)
    ghi_do(session, app_u.id, GiaiDoanDo.pre, 5.0, nhom=NhomThuNghiem.app)
    ghi_do(session, app_u.id, GiaiDoanDo.post, 8.0, nhom=NhomThuNghiem.app)
    # Nhóm đối chứng: pre 5 → post 6 (gain 1)
    ghi_do(session, ctrl_u.id, GiaiDoanDo.pre, 5.0, nhom=NhomThuNghiem.doi_chung)
    ghi_do(session, ctrl_u.id, GiaiDoanDo.post, 6.0, nhom=NhomThuNghiem.doi_chung)
    session.commit()

    g = learning_gain(session)
    assert g["app"]["gain"] == 3.0
    assert g["doi_chung"]["gain"] == 1.0
    # App cải thiện hơn đối chứng → đúng kỳ vọng thiết kế


def test_dashboard_khong_co_engagement(session):
    d = dashboard(session)
    assert "learning_gain" in d
    assert "chi_phi_token" in d
    assert "ty_le_tu_giai" in d
    # CHỦ Ý: không dùng engagement làm KPI hiệu quả (NFR-50)
    assert "engagement" not in d


# ---- API ----
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


def test_dashboard_chi_quan_tri(client):
    hs = _auth(client, "hs2@x.com")
    assert client.get("/metrics/dashboard", headers=hs).status_code == 403
    admin = _auth(client, "ad@x.com", vai_tro="quan_tri")
    r = client.get("/metrics/dashboard", headers=admin)
    assert r.status_code == 200
    assert "learning_gain" in r.json()
