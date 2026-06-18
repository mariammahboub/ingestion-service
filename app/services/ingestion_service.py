import logging
from app.domain.entities import SensorReading
from app.domain.exceptions import DuplicateReadingError, ReadingPersistenceError
from app.repositories.sensor_reading_repository import SensorReadingRepository
from app.schemas.sensor_reading import SensorReadingIn

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, repository: SensorReadingRepository):
        self.repository = repository

    def ingest(self, payload: SensorReadingIn):
        logger.info(
            "Ingesting reading | sensor_id=%s | timestamp=%s",
            payload.sensor_id,
            payload.timestamp,
        )

        reading = SensorReading(
            sensor_id=payload.sensor_id,
            timestamp=payload.timestamp,
            reading=payload.reading,
        )

        try:
            result = self.repository.add(reading)
            logger.info(
                "Reading stored successfully | id=%s | sensor_id=%s",
                result.id,
                result.sensor_id,
            )
            return result

        except DuplicateReadingError:
            logger.warning(
                "Duplicate reading rejected | sensor_id=%s | timestamp=%s",
                payload.sensor_id,
                payload.timestamp,
            )
            raise

        except ReadingPersistenceError as e:
            logger.error(
                "Persistence failure | sensor_id=%s | cause=%s",
                payload.sensor_id,
                e.cause,
                exc_info=True,
            )
            raise

    def get_readings(self, sensor_id: str, limit: int = 100):
        if limit < 1 or limit > 1000:
            raise ValueError(f"limit must be between 1 and 1000, got {limit}")

        logger.info("Fetching readings | sensor_id=%s | limit=%s", sensor_id, limit)

        try:
            results = self.repository.list_by_sensor(sensor_id, limit)
            logger.info("Fetched %d readings | sensor_id=%s", len(results), sensor_id)
            return results

        except ReadingPersistenceError as e:
            logger.error(
                "Failed to fetch readings | sensor_id=%s | cause=%s",
                sensor_id,
                e.cause,
                exc_info=True,
            )
            raise