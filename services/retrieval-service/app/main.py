"""
Retrieval Service - FastAPI Application Bootstrap.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.config import Settings, get_settings
from app.logging import configure_logging, get_logger
from app.kafka_handler import get_kafka_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    configure_logging()
    logger = get_logger(__name__)

    settings = get_settings()
    logger.info(
        f"Starting {settings.service_name} v{settings.service_version} "
        f"(env: {settings.environment})"
    )

    # Start Kafka consumer
    kafka_handler = get_kafka_handler()
    await kafka_handler.start()
    
    # Run consumer in background
    consumer_task = asyncio.create_task(kafka_handler.run())
    logger.info("Retrieval Kafka consumer started in background")

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
        title="WaqediAI Retrieval Service",
        description="Semantic Search & Vector Retrieval",
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc: Exception) -> JSONResponse:
        logger = get_logger(__name__)
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

    app.include_router(router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
