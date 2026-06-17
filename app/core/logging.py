import logging
import sys
from app.core.config import settings

LOG_FORMAT_DEV = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_FORMAT_PROD = "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"

def setup_logging() -> None:

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = LOG_FORMAT_DEV if settings.DEBUG else LOG_FORMAT_PROD

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized | level=%s | debug=%s",
        logging.getLevelName(log_level),
        settings.DEBUG,
    )