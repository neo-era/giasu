from typing import Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixin import IdMixin, TimestampMixin
from app.models.enums import MucDoHoc, PhanKhuc, TrangThaiNguoiDung, VaiTro


class NguoiDung(IdMixin, TimestampMixin, Base):
    __tablename__ = "nguoi_dung"

    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    so_dien_thoai: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255))
    vai_tro: Mapped[VaiTro] = mapped_column(Enum(VaiTro), default=VaiTro.hoc_sinh, nullable=False)
    trang_thai: Mapped[TrangThaiNguoiDung] = mapped_column(
        Enum(TrangThaiNguoiDung), default=TrangThaiNguoiDung.cho_xac_thuc, nullable=False
    )
    # An toàn vị thành niên + đồng ý phụ huynh (FR-C03, NFR-31)
    la_vi_thanh_nien: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dong_y_phu_huynh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ho_so: Mapped[Optional["HoSoHocSinh"]] = relationship(
        back_populates="nguoi_dung", uselist=False
    )


class HoSoHocSinh(IdMixin, TimestampMixin, Base):
    __tablename__ = "ho_so_hoc_sinh"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), unique=True, nullable=False
    )
    phan_khuc: Mapped[PhanKhuc] = mapped_column(
        Enum(PhanKhuc), default=PhanKhuc.dai_tra, nullable=False
    )
    lop: Mapped[int | None] = mapped_column(Integer)
    mon: Mapped[str | None] = mapped_column(String(50))
    doi_tuyen: Mapped[str | None] = mapped_column(String(100))
    muc_do: Mapped[MucDoHoc | None] = mapped_column(Enum(MucDoHoc))

    nguoi_dung: Mapped["NguoiDung"] = relationship(back_populates="ho_so")
