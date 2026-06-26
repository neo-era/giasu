from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin
from app.models.enums import PhamViKiemChung, PhuongPhapKiemChung, TrangThaiKiemChung


class KetQuaKiemChung(IdMixin, Base):
    """Nhật ký kiểm chứng một lời giải / tin nhắn (FR-C08, FR-L08)."""

    __tablename__ = "ket_qua_kiem_chung"

    tin_nhan_id: Mapped[str | None] = mapped_column(ForeignKey("tin_nhan.id"), index=True)
    loi_giai_id: Mapped[str | None] = mapped_column(ForeignKey("loi_giai.id"), index=True)
    phuong_phap: Mapped[PhuongPhapKiemChung] = mapped_column(
        Enum(PhuongPhapKiemChung), nullable=False
    )
    trang_thai: Mapped[TrangThaiKiemChung] = mapped_column(Enum(TrangThaiKiemChung), nullable=False)
    # Trung thực phạm vi: chỉ phần TÍNH TOÁN mới được coi là "đã kiểm" (FR-L08)
    pham_vi_da_kiem: Mapped[PhamViKiemChung] = mapped_column(
        Enum(PhamViKiemChung), default=PhamViKiemChung.tinh_toan, nullable=False
    )
    do_tin_cay: Mapped[float | None] = mapped_column(Float)
    can_nguoi_duyet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    chi_tiet: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
