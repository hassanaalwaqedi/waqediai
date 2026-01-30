"""
Ingestion Service - FastAPI Application Entry Point

Document Ingestion & Lifecycle Service for WaqediAI.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingestion_service.adapters import get_storage_adapter
from ingestion_service.api import documents_router
from ingestion_service.config import Settings, get_settings
from ingestion_service.services.events import close_producer


def configure_logging(settings: Settings) -> None:
    """Configure structured logging."""
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    settings = get_settings()
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Starting {settings.service_name} v{settings.service_version} "
        f"(env: {settings.environment})"
    )

    # Ensure storage bucket exists
    try:
        storage = get_storage_adapter()
        await storage.ensure_bucket_exists()
        logger.info(f"Storage bucket '{settings.storage_bucket}' ready")
    except Exception as e:
        logger.warning(f"Could not ensure bucket exists: {e}")

    yield

    # Cleanup
    await close_producer()
    logger.info(f"Shutting down {settings.service_name}")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory."""
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="WaqediAI Ingestion Service",
        description="Document Ingestion & Lifecycle Service",
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID middleware
    @app.middleware("http")
    async def add_correlation_id(request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger = logging.getLogger(__name__)
        logger.exception(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "type": "urn:waqedi:error:internal-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": str(exc) if settings.debug else "An unexpected error occurred",
            },
        )

    # Health check endpoints
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "healthy", "service": settings.service_name}

    @app.get("/ready", tags=["Health"])
    async def readiness_check() -> dict:
        return {"status": "ready", "service": settings.service_name}

    # Include API routes
    app.include_router(documents_router, prefix="/api/v1")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "ingestion_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
