from typing import Any

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base_mixin import IdMixin, TimestampMixin
from app.models.enums import CapDo, DoKho


class DeBai(IdMixin, TimestampMixin, Base):
    __tablename__ = "de_bai"

    mon: Mapped[str] = mapped_column(String(50), nullable=False)
    cap_do: Mapped[CapDo] = mapped_column(Enum(CapDo), default=CapDo.thpt, nullable=False)
    lop: Mapped[int | None] = mapped_column(Integer)
    chuong: Mapped[str | None] = mapped_column(String(100))
    do_kho: Mapped[DoKho | None] = mapped_column(Enum(DoKho))
    nguon: Mapped[str | None] = mapped_column(String(255))
    de_latex: Mapped[str] = mapped_column(Text, nullable=False)

    loi_giai: Mapped[list["LoiGiai"]] = relationship(
        back_populates="de_bai", cascade="all, delete-orphan"
    )


class LoiGiai(IdMixin, TimestampMixin, Base):
    __tablename__ = "loi_giai"

    de_bai_id: Mapped[str] = mapped_column(ForeignKey("de_bai.id"), nullable=False, index=True)
    cac_buoc: Mapped[list[Any] | None] = mapped_column(JSON)
    dap_so: Mapped[str | None] = mapped_column(String(255))
    nguon: Mapped[str | None] = mapped_column(String(255))
    la_mau: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    de_bai: Mapped["DeBai"] = relationship(back_populates="loi_giai")
