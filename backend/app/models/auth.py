from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin
from app.models.enums import MucDichOTP


class MaXacThuc(IdMixin, Base):
    """Mã OTP cho đăng ký/đăng nhập (FR-C01). Lưu DẠNG HASH, có hạn dùng."""

    __tablename__ = "ma_xac_thuc"

    dinh_danh: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    ma_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    muc_dich: Mapped[MucDichOTP] = mapped_column(Enum(MucDichOTP), nullable=False)
    het_han: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    da_dung: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
