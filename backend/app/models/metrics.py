from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin
from app.models.enums import GiaiDoanDo, NhomThuNghiem


class DoLuongHoc(IdMixin, Base):
    """Điểm đo learning gain (đo khi TẮT AI) — chuẩn vàng NFR-50/51.

    KHÔNG đo engagement; chỉ đo năng lực tự làm (pre/post/retention).
    """

    __tablename__ = "do_luong_hoc"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    giai_doan: Mapped[GiaiDoanDo] = mapped_column(Enum(GiaiDoanDo), nullable=False)
    diem: Mapped[float] = mapped_column(Float, nullable=False)
    tat_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    nhom: Mapped[NhomThuNghiem] = mapped_column(
        Enum(NhomThuNghiem), default=NhomThuNghiem.app, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
