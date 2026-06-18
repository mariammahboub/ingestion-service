import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.domain.exceptions import DuplicateReadingError, ReadingPersistenceError, SensorNotFoundError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:

        logger.warning(
            "Validation error | method=%s | path=%s | errors=%s",
            request.method,
            request.url.path,
            exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Request validation failed.",
                "errors": [
                    {
                        "field": " -> ".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"],
                        "type": err["type"],
                    }
                    for err in exc.errors()
                ],
            },
        )

    @app.exception_handler(DuplicateReadingError)
    async def duplicate_reading_handler(
        request: Request, exc: DuplicateReadingError
    ) -> JSONResponse:

        logger.warning(
            "Duplicate reading blocked | method=%s | path=%s | detail=%s",
            request.method,
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ReadingPersistenceError)
    async def persistence_error_handler(
        request: Request, exc: ReadingPersistenceError
    ) -> JSONResponse:
 
        logger.error(
            "Persistence failure | method=%s | path=%s | cause=%s",
            request.method,
            request.url.path,
            exc.cause,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A storage error occurred. The operation could not be completed."},
        )
    @app.exception_handler(SensorNotFoundError)
    async def sensor_not_found_handler(request: Request, exc: SensorNotFoundError) -> JSONResponse:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"detail": str(exc)},
                                )
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
  
        logger.critical(
            "Unhandled exception | method=%s | path=%s | error=%s",
            request.method,
            request.url.path,
            str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )
