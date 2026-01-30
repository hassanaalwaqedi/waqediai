"""
Auth Service - FastAPI Application Entry Point

Identity, Authentication & Authorization Service for WaqediAI.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth_service.config import Settings, get_settings
from auth_service.api import auth_router, users_router


def configure_logging(settings: Settings) -> None:
    """Configure structured logging."""
    log_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle.
    
    - Startup: Initialize database connections, logging
    - Shutdown: Close connections, cleanup
    """
    settings = get_settings()
    configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Starting {settings.service_name} v{settings.service_version} "
        f"(env: {settings.environment})"
    )

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection

    yield

    logger.info(f"Shutting down {settings.service_name}")
    # TODO: Close database connections
    # TODO: Close Redis connection


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Application factory.
    
    Args:
        settings: Optional settings override (useful for testing).
        
    Returns:
        Configured FastAPI application.
    """
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="WaqediAI Auth Service",
        description="Identity, Authentication & Authorization Service",
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
        """Basic health check - is the service running?"""
        return {"status": "healthy", "service": settings.service_name}

    @app.get("/ready", tags=["Health"])
    async def readiness_check() -> dict:
        """Readiness check - is the service ready to accept traffic?"""
        # TODO: Check database connection
        # TODO: Check Redis connection
        return {"status": "ready", "service": settings.service_name}

    # Include API routes
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")

    return app


# Create app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "auth_service.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
