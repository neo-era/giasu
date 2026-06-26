from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin
from app.models.enums import TrangThaiDuyet


class HangDoiDuyet(IdMixin, Base):
    """Mục chờ người duyệt (HITL) khi AI không tự khẳng định (FR-E05)."""

    __tablename__ = "hang_doi_duyet"

    loai: Mapped[str] = mapped_column(String(50), nullable=False)  # "cross_check"…
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    chi_tiet: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    trang_thai: Mapped[TrangThaiDuyet] = mapped_column(
        Enum(TrangThaiDuyet), default=TrangThaiDuyet.cho_duyet, nullable=False
    )
    ket_luan_nguoi: Mapped[str | None] = mapped_column(Text)
    nguoi_duyet_id: Mapped[str | None] = mapped_column(ForeignKey("nguoi_dung.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
