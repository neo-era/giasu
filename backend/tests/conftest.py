import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (đăng ký toàn bộ bảng vào metadata)
from app.db.base import Base


@pytest.fixture()
def session() -> Session:
    """DB SQLite in-memory dùng chung một connection cho cả phiên test."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestSession() as s:
        yield s
    Base.metadata.drop_all(engine)
