import pytest

from app.auth import otp
from app.billing.plans import dung_bac_re
from app.billing.service import (
    QuotaExceeded,
    kiem_va_dung_luot,
    lay_goi_hien_tai,
    tao_checkout,
    xac_nhan_thanh_toan,
)
from app.models import NguoiDung
from app.models.enums import LoaiGoi, TrangThaiNguoiDung, VaiTro

FIXED = "123456"


def _user(session) -> NguoiDung:
    u = NguoiDung(
        email="hs@x.com",
        vai_tro=VaiTro.hoc_sinh,
        trang_thai=TrangThaiNguoiDung.hoat_dong,
    )
    session.add(u)
    session.commit()
    return u


def test_free_luon_bac_re():
    assert dung_bac_re(LoaiGoi.free) is True
    assert dung_bac_re(LoaiGoi.premium) is False


def test_free_vuot_han_muc_bi_chan(session):
    u = _user(session)
    # Gói free mặc định = 5 câu/ngày
    for _ in range(5):
        kiem_va_dung_luot(session, u)
    with pytest.raises(QuotaExceeded):
        kiem_va_dung_luot(session, u)


def test_webhook_idempotent_nang_cap(session):
    u = _user(session)
    tt = tao_checkout(session, u, LoaiGoi.standard)
    assert lay_goi_hien_tai(session, u) == LoaiGoi.free

    xac_nhan_thanh_toan(session, tt.ma_giao_dich)
    assert lay_goi_hien_tai(session, u) == LoaiGoi.standard

    # Gọi lại webhook cùng mã → không nâng cấp/đổi gì (idempotent)
    from sqlalchemy import func, select

    from app.models import Goi

    so_goi_truoc = session.scalar(select(func.count()).select_from(Goi))
    xac_nhan_thanh_toan(session, tt.ma_giao_dich)
    so_goi_sau = session.scalar(select(func.count()).select_from(Goi))
    assert so_goi_truoc == so_goi_sau
    assert lay_goi_hien_tai(session, u) == LoaiGoi.standard


def test_premium_khong_gioi_han(session):
    u = _user(session)
    tt = tao_checkout(session, u, LoaiGoi.premium)
    xac_nhan_thanh_toan(session, tt.ma_giao_dich)
    # Premium không giới hạn → gọi nhiều lần không lỗi
    for _ in range(20):
        kiem_va_dung_luot(session, u)


# ---- API: vượt hạn mức trong chat → 429 ----


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr(otp, "generate_code", lambda: FIXED)


def test_chat_vuot_han_muc_429(client):
    email = "hs2@x.com"
    client.post("/auth/register", json={"email": email, "password": "matkhau123"})
    client.post("/auth/verify-otp", json={"dinh_danh": email, "ma": FIXED})
    tok = client.post("/auth/login", json={"dinh_danh": email, "password": "matkhau123"}).json()[
        "access_token"
    ]
    h = {"Authorization": f"Bearer {tok}"}
    cid = client.post("/chat/conversations", json={}, headers=h).json()["id"]

    codes = []
    for _ in range(7):  # free = 5/ngày
        r = client.post(f"/chat/conversations/{cid}/messages", json={"noi_dung": "hi"}, headers=h)
        codes.append(r.status_code)
    assert 429 in codes
    assert codes.count(200) == 5
