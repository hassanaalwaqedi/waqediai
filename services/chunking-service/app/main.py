"""
Chunking Service - FastAPI Application.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.config import Settings, get_settings
from app.kafka_handler import get_kafka_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    # Start Kafka consumer
    kafka_handler = get_kafka_handler()
    await kafka_handler.start()
    
    # Run consumer in background
    consumer_task = asyncio.create_task(kafka_handler.run())
    logger.info("Chunking Kafka consumer started in background")
    
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
        title="WaqediAI Chunking Service",
        description="Semantic Text Chunking for Knowledge Processing",
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
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
        return JSONResponse(
            status_code=500,
            content={
                "type": "urn:waqedi:error:internal-error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": str(exc) if settings.debug else "An error occurred",
            },
        )

    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
