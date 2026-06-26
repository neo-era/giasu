from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin


class KhaiNiemOn(IdMixin, Base):
    """Khái niệm/lỗi cần ôn tập truy hồi theo lịch giãn cách (FR-L05)."""

    __tablename__ = "khai_niem_on"
    __table_args__ = (
        UniqueConstraint("nguoi_dung_id", "khai_niem", name="uq_khai_niem_on_nguoi_kn"),
    )

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    khai_niem: Mapped[str] = mapped_column(String(255), nullable=False)
    so_lan_sai: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    so_lan_on: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lan_on_ke_tiep: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
