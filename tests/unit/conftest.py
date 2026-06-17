import pytest
from datetime import datetime, timezone

from app.db.models import SensorReadingModel
from app.domain.exceptions import DuplicateReadingError
from app.schemas.sensor_reading import SensorReadingIn
from app.services.ingestion_service import IngestionService


class FakeRepository:
    """In-memory fake — tests IngestionService with zero database involvement."""

    def __init__(self):
        self.store: list[SensorReadingModel] = []
        self.should_raise: Exception | None = None

    def add(self, reading) -> SensorReadingModel:
        if self.should_raise:
            raise self.should_raise

        for existing in self.store:
            if existing.sensor_id == reading.sensor_id and existing.timestamp == reading.timestamp:
                raise DuplicateReadingError(
                    f"Reading for sensor '{reading.sensor_id}' at {reading.timestamp} already exists."
                )

        model = SensorReadingModel(
            id=len(self.store) + 1,
            sensor_id=reading.sensor_id,
            timestamp=reading.timestamp,
            reading=reading.reading,
            received_at=datetime.now(timezone.utc),
        )
        self.store.append(model)
        return model

    def list_by_sensor(self, sensor_id: str, limit: int) -> list[SensorReadingModel]:
        if self.should_raise:
            raise self.should_raise
        return [r for r in self.store if r.sensor_id == sensor_id][:limit]


@pytest.fixture
def repo() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def service(repo) -> IngestionService:
    return IngestionService(repo)


@pytest.fixture
def make_payload():
    """Factory fixture for building valid SensorReadingIn payloads in tests."""
    def _make(
        sensor_id: str = "sensor-01",
        timestamp: datetime | None = None,
        reading: float = 23.5,
    ) -> SensorReadingIn:
        return SensorReadingIn(
            sensor_id=sensor_id,
            timestamp=timestamp or datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
            reading=reading,
        )
    return _make