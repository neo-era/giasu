from datetime import timedelta

from app.auth import otp
from app.models.enums import MucDichOTP


def test_otp_ok(session):
    code = otp.create_otp(session, "a@x.com", MucDichOTP.dang_ky)
    assert otp.verify_otp(session, "a@x.com", code, MucDichOTP.dang_ky) == "ok"


def test_otp_sai(session):
    otp.create_otp(session, "a@x.com", MucDichOTP.dang_ky)
    assert otp.verify_otp(session, "a@x.com", "000000", MucDichOTP.dang_ky) == "sai"


def test_otp_het_han(session):
    code = otp.create_otp(session, "a@x.com", MucDichOTP.dang_ky)
    # Đẩy hạn về quá khứ
    rec = session.query(otp.MaXacThuc).filter_by(dinh_danh="a@x.com").one()
    rec.het_han = otp._now() - timedelta(minutes=1)
    session.flush()
    assert otp.verify_otp(session, "a@x.com", code, MucDichOTP.dang_ky) == "het_han"


def test_otp_da_dung_khong_tai_su_dung(session):
    code = otp.create_otp(session, "a@x.com", MucDichOTP.dang_ky)
    assert otp.verify_otp(session, "a@x.com", code, MucDichOTP.dang_ky) == "ok"
    # Lần 2: đã đánh dấu da_dung → không còn bản ghi hợp lệ
    assert otp.verify_otp(session, "a@x.com", code, MucDichOTP.dang_ky) == "khong_tim_thay"
