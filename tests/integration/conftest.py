import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db, Base
from app.api.dependencies import get_ingestion_service
from app.repositories.sensor_reading_repository import SqlAlchemySensorReadingRepository
from app.services.ingestion_service import IngestionService


# In-memory database — no files, no cleanup, no risk of accidentally committing test data.
# StaticPool is required so the in-memory DB is shared across all connections in the pool.
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_ingestion_service():
    db = TestSessionLocal()
    try:
        repo = SqlAlchemySensorReadingRepository(db)
        yield IngestionService(repo)
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test, drop them after — full isolation between tests."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ingestion_service] = override_get_ingestion_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()