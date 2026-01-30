"""
Reasoning Service - FastAPI Application Bootstrap.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.config import Settings, get_settings
from app.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle."""
    configure_logging()
    logger = get_logger(__name__)

    settings = get_settings()
    logger.info(
        f"Starting {settings.service_name} v{settings.service_version} "
        f"(env: {settings.environment}, model: {settings.ollama_model})"
    )

    yield

    logger.info(f"Shutting down {settings.service_name}")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory."""
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="WaqediAI Reasoning Service",
        description="AI Reasoning with Citation-Backed Responses",
        version=settings.service_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS
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

    # Include routes
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
