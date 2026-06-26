from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixin import IdMixin, TimestampMixin
from app.models.enums import PhanKhuc, VaiTinNhan


class HoiThoai(IdMixin, TimestampMixin, Base):
    __tablename__ = "hoi_thoai"

    nguoi_dung_id: Mapped[str] = mapped_column(
        ForeignKey("nguoi_dung.id"), nullable=False, index=True
    )
    phan_khuc: Mapped[PhanKhuc] = mapped_column(
        Enum(PhanKhuc), default=PhanKhuc.dai_tra, nullable=False
    )
    chu_de: Mapped[str | None] = mapped_column(String(255))

    tin_nhan: Mapped[list["TinNhan"]] = relationship(
        back_populates="hoi_thoai", cascade="all, delete-orphan"
    )


class TinNhan(IdMixin, Base):
    __tablename__ = "tin_nhan"

    hoi_thoai_id: Mapped[str] = mapped_column(
        ForeignKey("hoi_thoai.id"), nullable=False, index=True
    )
    vai: Mapped[VaiTinNhan] = mapped_column(Enum(VaiTinNhan), nullable=False)
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    anh_url: Mapped[str | None] = mapped_column(String(500))
    # Định tuyến + giám sát chi phí token theo phân khúc (FR-C11)
    model_dung: Mapped[str | None] = mapped_column(String(100))
    token_vao: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_ra: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    hoi_thoai: Mapped["HoiThoai"] = relationship(back_populates="tin_nhan")
