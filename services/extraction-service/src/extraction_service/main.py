"""
Extraction Service - FastAPI Application.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from extraction_service.config import Settings, get_settings
from extraction_service.adapters.kafka_handler import get_kafka_handler


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

    # Start Kafka consumer
    kafka_handler = get_kafka_handler()
    await kafka_handler.start()
    
    # Run consumer in background task
    consumer_task = asyncio.create_task(kafka_handler.run())
    logger.info("Kafka consumer started in background")

    yield

    # Shutdown
    await kafka_handler.stop()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    logger.info(f"Shutting down {settings.service_name}")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory."""
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="WaqediAI Extraction Service",
        description="OCR & Speech-to-Text Extraction Service",
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc: Exception) -> JSONResponse:
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

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "extraction_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
