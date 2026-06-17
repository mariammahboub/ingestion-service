from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.db.session import engine
from app.db import models
from app.api.routes import router

# Boot sequence — order matters
setup_logging()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Entry point for environmental readings sent by external sensors.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(router)


@app.get("/", tags=["Health"], summary="Root status check")
def root() -> dict:
    return {"status": "ok"}


@app.get("/health", tags=["Health"], summary="Service health check")
def health_check() -> dict:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }