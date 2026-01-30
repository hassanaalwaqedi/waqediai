"""
Service Template - FastAPI Application Entry Point

This is the main entry point for the service. Copy and customize
for each new service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from service_name.config import Settings, get_settings
from service_name.api.routes import router

# Import from shared libraries (adjust path after creating service)
# from libs.common import WaqediError
# from libs.observability import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application lifecycle.

    - Startup: Initialize connections, load resources
    - Shutdown: Close connections, cleanup
    """
    settings = get_settings()

    # Startup
    # configure_logging(settings.service_name, settings.log_level)
    # logger = get_logger(__name__)
    # logger.info("Service starting", extra={"version": settings.service_version})

    print(f"Starting {settings.service_name} v{settings.service_version}")

    yield

    # Shutdown
    # logger.info("Service shutting down")
    print(f"Shutting down {settings.service_name}")


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
        title=settings.service_name,
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

    # Exception handler for custom errors
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # if isinstance(exc, WaqediError):
        #     return JSONResponse(
        #         status_code=exc.status_code,
        #         content=exc.to_problem_details(),
        #     )
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
    @app.get(settings.health_check_path, tags=["Health"])
    async def health_check() -> dict:
        """Basic health check - is the service running?"""
        return {"status": "healthy", "service": settings.service_name}

    @app.get(settings.ready_check_path, tags=["Health"])
    async def readiness_check() -> dict:
        """Readiness check - is the service ready to accept traffic?"""
        # TODO: Add dependency checks (database, cache, etc.)
        return {"status": "ready", "service": settings.service_name}

    # Include API routes
    app.include_router(router, prefix="/api/v1")

    return app


# Create app instance for uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "service_name.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
