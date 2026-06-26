from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base_mixin import IdMixin


class TaiLieu(IdMixin, Base):
    """Tài liệu tri thức cho RAG (FR-E08). Chỉ nạp nguồn HỢP PHÁP, có trích dẫn.

    embedding lưu JSON (list[float]) để chạy được trên cả SQLite/Postgres; có thể
    chuyển sang cột pgvector + chỉ mục ANN khi tối ưu sau.
    """

    __tablename__ = "tai_lieu"

    nguon: Mapped[str] = mapped_column(String(255), nullable=False)
    noi_dung: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
