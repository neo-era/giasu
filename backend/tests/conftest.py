import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (đăng ký toàn bộ bảng vào metadata)
from app.db.base import Base
from app.db.session import get_db
from main import app


def _memory_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


@pytest.fixture()
def session() -> Session:
    """DB SQLite in-memory dùng chung một connection cho cả phiên test."""
    engine = _memory_engine()
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestSession() as s:
        yield s
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client() -> TestClient:
    """TestClient với get_db trỏ vào DB SQLite in-memory riêng cho mỗi test."""
    engine = _memory_engine()
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
