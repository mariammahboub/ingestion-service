from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.domain.entities import SensorReading
from app.domain.exceptions import DuplicateReadingError, ReadingPersistenceError
from app.db.models import SensorReadingModel


@runtime_checkable
class SensorReadingRepository(Protocol):

    def add(self, reading: SensorReading) -> SensorReadingModel: ...
    def list_by_sensor(self, sensor_id: str, limit: int) -> list[SensorReadingModel]: ...


class SqlAlchemySensorReadingRepository:
    """Concrete SQLAlchemy implementation of SensorReadingRepository."""

    def __init__(self, db: Session):
        self.db = db

    def add(self, reading: SensorReading) -> SensorReadingModel:
        model = SensorReadingModel(
            sensor_id=reading.sensor_id,
            timestamp=reading.timestamp,
            reading=reading.reading,
            received_at=datetime.now(timezone.utc),
        )
        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model

        except IntegrityError:
            # Unique constraint violated — sensor retried, expected behavior.
            self.db.rollback()
            raise DuplicateReadingError(
                f"Reading for sensor '{reading.sensor_id}' at {reading.timestamp} already exists."
            )

        except SQLAlchemyError as e:
            # Anything else: connection lost, deadlock, disk full, etc.
            self.db.rollback()
            raise ReadingPersistenceError(cause=e)

    def list_by_sensor(self, sensor_id: str, limit: int) -> list[SensorReadingModel]:
        try:
            return (
                self.db.query(SensorReadingModel)
                .filter(SensorReadingModel.sensor_id == sensor_id)
                .order_by(SensorReadingModel.timestamp.desc())
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            raise ReadingPersistenceError(cause=e)