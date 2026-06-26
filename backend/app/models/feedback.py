from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixin import IdMixin, TimestampMixin
from app.models.enums import (
    ChuDePhanAnh,
    TrangThaiKiemDuyet,
    TrangThaiPhanAnh,
    VaiTro,
)


class PhanAnh(IdMixin, TimestampMixin, Base):
    """Phản ánh dạng blog (FR-F01/F02). Cho phép ẩn danh; có kiểm duyệt (FR-F08)."""

    __tablename__ = "phan_anh"

    nguoi_gui_id: Mapped[str | None] = mapped_column(ForeignKey("nguoi_dung.id"), index=True)
    an_danh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    chu_de: Mapped[ChuDePhanAnh] = mapped_column(Enum(ChuDePhanAnh), nullable=False)
    tieu_de: Mapped[str] = mapped_column(String(255), nullable=False)
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    anh_url: Mapped[str | None] = mapped_column(String(500))
    trang_thai: Mapped[TrangThaiPhanAnh] = mapped_column(
        Enum(TrangThaiPhanAnh), default=TrangThaiPhanAnh.moi, nullable=False
    )
    trang_thai_kiem_duyet: Mapped[TrangThaiKiemDuyet] = mapped_column(
        Enum(TrangThaiKiemDuyet), default=TrangThaiKiemDuyet.cho_duyet, nullable=False
    )
    so_dong_tinh: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Liên kết phản ánh "lỗi lời giải" với hàng đợi kiểm chứng (FR-F09)
    loi_giai_id: Mapped[str | None] = mapped_column(ForeignKey("loi_giai.id"), index=True)

    binh_luan: Mapped[list["BinhLuan"]] = relationship(
        back_populates="phan_anh", cascade="all, delete-orphan"
    )


class BinhLuan(IdMixin, Base):
    """Phản hồi đội ngũ (chính thức) hoặc bình luận cộng đồng (FR-F05/F03)."""

    __tablename__ = "binh_luan"

    phan_anh_id: Mapped[str] = mapped_column(ForeignKey("phan_anh.id"), nullable=False, index=True)
    nguoi_dang_id: Mapped[str | None] = mapped_column(ForeignKey("nguoi_dung.id"), index=True)
    vai_tro_nguoi_dang: Mapped[VaiTro | None] = mapped_column(Enum(VaiTro))
    la_phan_hoi_chinh_thuc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    trang_thai_kiem_duyet: Mapped[TrangThaiKiemDuyet] = mapped_column(
        Enum(TrangThaiKiemDuyet), default=TrangThaiKiemDuyet.cho_duyet, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    phan_anh: Mapped["PhanAnh"] = relationship(back_populates="binh_luan")
