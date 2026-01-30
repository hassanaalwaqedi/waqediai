"""Adapters package."""

from ingestion_service.adapters.database import Base, get_session
from ingestion_service.adapters.repository import DocumentRepository
from ingestion_service.adapters.storage import (
    S3StorageAdapter,
    StorageResult,
    build_storage_key,
    get_storage_adapter,
)

__all__ = [
    "get_session",
    "Base",
    "DocumentRepository",
    "S3StorageAdapter",
    "get_storage_adapter",
    "build_storage_key",
    "StorageResult",
]
