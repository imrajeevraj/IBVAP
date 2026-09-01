"""Deterministic test database lifecycle for the backend suite."""

import os
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATABASE = PROJECT_ROOT / ".pytest_ibvap.db"

# Set before application modules are imported during test collection.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "pytest-secret-with-at-least-32-characters"
os.environ["ADMIN_USERNAME"] = ""
os.environ["ADMIN_PASSWORD"] = ""


@pytest.fixture(scope="function")
def engine():
    """Create a completely fresh, isolated database engine for each test."""
    # We use StaticPool because SQLite in-memory databases are per-connection.
    # FastAPI test clients might use different threads, so we need a static pool
    # so all threads in the test share the same memory database connection.
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    from backend.app.models import Base
    import backend.app.models  # noqa: F401 - registers every SQLAlchemy model
    
    # TEST-ONLY SCHEMA BOOTSTRAP
    # We use create_all instead of Alembic because the production schema uses
    # PostgreSQL-specific extensions (like pgvector) which Alembic migrations
    # correctly include but SQLite does not support. 
    # This DOES NOT validate Alembic migrations.
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a fresh database session for the test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    """Automatically override the FastAPI get_db dependency for all tests."""
    from backend.app.main import app
    from backend.app.core.database import get_db

    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    yield
    app.dependency_overrides.clear()
