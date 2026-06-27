import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (đăng ký toàn bộ bảng vào metadata)
from app.db.base import Base
from app.db.session import get_db
from main import app


# Bậc model dùng cho test — LUÔN là mock, độc lập với .env của môi trường dev.
_MOCK_TIERS = {
    "re": "mock:mock-fast",
    "can_bang": "mock:mock-balanced",
    "reasoning": "mock:mock-reasoning",
    "vision": "mock:mock-vision",
}


@pytest.fixture(autouse=True)
def _llm_defaults():
    """Mỗi test bắt đầu với registry mock + tiers mock + cache service sạch.

    Ép tiers mock để test KHÔNG phụ thuộc cấu hình LLM thật trong .env, và tránh
    rò trạng thái giữa các test có reset_registry/đổi runtime tiers."""
    from app.llm.providers import init_default_providers
    from app.llm.registry import reset_registry
    from app.llm.service import get_llm_service
    from app.runtime_config import set_tiers

    reset_registry()
    init_default_providers()
    set_tiers(_MOCK_TIERS)
    get_llm_service.cache_clear()
    yield


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
