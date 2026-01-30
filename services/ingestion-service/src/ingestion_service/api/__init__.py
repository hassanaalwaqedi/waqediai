"""API package."""

from ingestion_service.api.routes.documents import router as documents_router

__all__ = ["documents_router"]
