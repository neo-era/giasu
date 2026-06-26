import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.config import settings
from app.models.auth import MaXacThuc
from app.models.enums import MucDichOTP


def _now() -> datetime:
    """UTC dạng naive — đồng nhất giữa SQLite (test) và Postgres."""
    return datetime.now(UTC).replace(tzinfo=None)


def generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(settings.otp_length))


def send_otp(dinh_danh: str, code: str) -> None:
    """Gửi OTP (SMS/email). Bản dev: log ra console. KHÔNG trả OTP qua API."""
    if settings.debug:
        print(f"[OTP][dev] {dinh_danh} -> {code}")


def create_otp(db: Session, dinh_danh: str, muc_dich: MucDichOTP) -> str:
    code = generate_code()
    rec = MaXacThuc(
        dinh_danh=dinh_danh,
        ma_hash=hash_password(code),
        muc_dich=muc_dich,
        het_han=_now() + timedelta(minutes=settings.otp_expire_minutes),
    )
    db.add(rec)
    db.flush()
    return code


def verify_otp(db: Session, dinh_danh: str, code: str, muc_dich: MucDichOTP) -> str:
    """Trả 'ok' | 'het_han' | 'sai' | 'khong_tim_thay'."""
    rec = db.scalar(
        select(MaXacThuc)
        .where(
            MaXacThuc.dinh_danh == dinh_danh,
            MaXacThuc.muc_dich == muc_dich,
            MaXacThuc.da_dung.is_(False),
        )
        .order_by(MaXacThuc.created_at.desc())
    )
    if rec is None:
        return "khong_tim_thay"
    if rec.het_han < _now():
        return "het_han"
    if not verify_password(code, rec.ma_hash):
        return "sai"
    rec.da_dung = True
    db.flush()
    return "ok"
