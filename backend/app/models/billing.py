from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin, TimestampMixin
from app.models.enums import (
    LoaiGoi,
    PhuongThucThanhToan,
    TrangThaiGoi,
    TrangThaiThanhToan,
)


class Goi(IdMixin, TimestampMixin, Base):
    __tablename__ = "goi"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    loai: Mapped[LoaiGoi] = mapped_column(Enum(LoaiGoi), default=LoaiGoi.free, nullable=False)
    trang_thai: Mapped[TrangThaiGoi] = mapped_column(
        Enum(TrangThaiGoi), default=TrangThaiGoi.hoat_dong, nullable=False
    )
    bat_dau: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ket_thuc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class HanMuc(IdMixin, Base):
    """Hạn mức sử dụng theo ngày (siết gói free — FR-M06, NFR-40)."""

    __tablename__ = "han_muc"
    __table_args__ = (UniqueConstraint("nguoi_dung_id", "ngay", name="uq_han_muc_nguoi_ngay"),)

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    ngay: Mapped[date] = mapped_column(Date, nullable=False)
    so_cau_da_dung: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gioi_han: Mapped[int] = mapped_column(Integer, nullable=False)


class ThanhToan(IdMixin, Base):
    __tablename__ = "thanh_toan"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    so_tien: Mapped[int] = mapped_column(Integer, nullable=False)  # VND
    phuong_thuc: Mapped[PhuongThucThanhToan] = mapped_column(
        Enum(PhuongThucThanhToan), default=PhuongThucThanhToan.vietqr, nullable=False
    )
    trang_thai: Mapped[TrangThaiThanhToan] = mapped_column(
        Enum(TrangThaiThanhToan), default=TrangThaiThanhToan.cho, nullable=False
    )
    ma_giao_dich: Mapped[str | None] = mapped_column(String(100), unique=True)
    # Gói mà giao dịch này mua (để nâng cấp khi xác nhận)
    goi_muon: Mapped[LoaiGoi | None] = mapped_column(Enum(LoaiGoi))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
