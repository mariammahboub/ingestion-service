from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Application
    APP_NAME: str = "Environmental Metrics Ingestion Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./sensor_data.db"

    # Query limits
    MAX_READING_LIMIT: int = 1000
    DEFAULT_READING_LIMIT: int = 100

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8",
    }

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()