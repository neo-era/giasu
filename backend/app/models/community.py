from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin


class DongTinh(IdMixin, Base):
    """'Tôi cũng gặp' — đồng tình một phản ánh (FR-F04). Mỗi người 1 lần."""

    __tablename__ = "dong_tinh"
    __table_args__ = (
        UniqueConstraint("nguoi_dung_id", "phan_anh_id", name="uq_dong_tinh_nguoi_pa"),
    )

    nguoi_dung_id: Mapped[str] = mapped_column(ForeignKey("nguoi_dung.id"), nullable=False)
    phan_anh_id: Mapped[str] = mapped_column(ForeignKey("phan_anh.id"), nullable=False, index=True)


class ThongBao(IdMixin, Base):
    """Thông báo cho người dùng (FR-F10)."""

    __tablename__ = "thong_bao"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    da_doc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class BoHoiQuy(IdMixin, Base):
    """Ca lỗi đã sửa → bổ sung bộ hồi quy để không tái diễn (FR-F09)."""

    __tablename__ = "bo_hoi_quy"

    nguon_phan_anh_id: Mapped[str | None] = mapped_column(ForeignKey("phan_anh.id"))
    mo_ta: Mapped[str] = mapped_column(Text, nullable=False)
    nhan: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
