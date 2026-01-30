"""
Database adapter for document metadata.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ingestion_service.config import get_settings
from ingestion_service.domain.models import (
    Document,
    DocumentStatus,
    FileCategory,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class DocumentModel(Base):
    """Document database model."""

    __tablename__ = "documents"
    __table_args__ = {"schema": "documents"}

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    uploaded_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    department_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    collection_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    file_category: Mapped[str] = mapped_column(String(20), nullable=False)
    language: Mapped[str | None] = mapped_column(String(10))

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="UPLOADED")
    retention_policy: Mapped[str] = mapped_column(String(50), nullable=False, default="standard")
    legal_hold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    storage_bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    custom_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    def to_domain(self) -> Document:
        return Document(
            id=self.id,
            tenant_id=self.tenant_id,
            uploaded_by=self.uploaded_by,
            department_id=self.department_id,
            collection_id=self.collection_id,
            filename=self.filename,
            content_type=self.content_type,
            size_bytes=self.size_bytes,
            checksum_sha256=self.checksum_sha256,
            file_category=FileCategory(self.file_category),
            language=self.language,
            status=DocumentStatus(self.status),
            retention_policy=self.retention_policy,
            legal_hold=self.legal_hold,
            storage_bucket=self.storage_bucket,
            storage_key=self.storage_key,
            uploaded_at=self.uploaded_at,
            validated_at=self.validated_at,
            processed_at=self.processed_at,
            archived_at=self.archived_at,
            deleted_at=self.deleted_at,
            expires_at=self.expires_at,
            metadata=self.custom_metadata or {},
        )

    @classmethod
    def from_domain(cls, doc: Document) -> "DocumentModel":
        return cls(
            id=doc.id,
            tenant_id=doc.tenant_id,
            uploaded_by=doc.uploaded_by,
            department_id=doc.department_id,
            collection_id=doc.collection_id,
            filename=doc.filename,
            content_type=doc.content_type,
            size_bytes=doc.size_bytes,
            checksum_sha256=doc.checksum_sha256,
            file_category=doc.file_category.value,
            language=doc.language,
            status=doc.status.value,
            retention_policy=doc.retention_policy,
            legal_hold=doc.legal_hold,
            storage_bucket=doc.storage_bucket,
            storage_key=doc.storage_key,
            uploaded_at=doc.uploaded_at or datetime.now(UTC),
            validated_at=doc.validated_at,
            processed_at=doc.processed_at,
            archived_at=doc.archived_at,
            deleted_at=doc.deleted_at,
            expires_at=doc.expires_at,
            custom_metadata=doc.metadata,
        )


# Database connection management
_engine = None
_session_factory = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url.get_secret_value(),
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
