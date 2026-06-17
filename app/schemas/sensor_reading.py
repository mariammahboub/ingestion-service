import math
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class SensorReadingIn(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=128, description="Unique sensor identifier")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of when the reading was taken")
    reading: float = Field(..., description="The environmental measurement value")

    @field_validator("sensor_id")
    @classmethod
    def sensor_id_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("sensor_id cannot be blank or whitespace only")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_have_timezone_and_not_be_future(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must include timezone info (e.g. 2024-01-15T10:30:00Z)")
        if v > datetime.now(timezone.utc):
            raise ValueError("timestamp cannot be in the future")
        return v

    @field_validator("reading")
    @classmethod
    def reading_must_be_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("reading must be a finite number, not NaN or Infinity")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "sensor_id": "sensor-cairo-01",
                "timestamp": "2024-01-15T10:30:00Z",
                "reading": 23.5,
            }
        }
    }


class SensorReadingOut(BaseModel):
    id: int
    sensor_id: str
    timestamp: datetime
    reading: float
    received_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "sensor_id": "sensor-cairo-01",
                "timestamp": "2024-01-15T10:30:00Z",
                "reading": 23.5,
                "received_at": "2024-01-15T10:30:01.123Z",
            }
        }
    }