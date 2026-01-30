"""
Database adapter for extraction results.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, Integer, String, Text, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from extraction_service.config import get_settings
from extraction_service.domain import (
    ExtractionResult,
    ExtractionType,
)


class Base(DeclarativeBase):
    pass


class ExtractionJobModel(Base):
    """Extraction job database model."""

    __tablename__ = "jobs"
    __table_args__ = {"schema": "extraction"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(50), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ExtractionResultModel(Base):
    """Extraction result database model."""

    __tablename__ = "results"
    __table_args__ = {"schema": "extraction"}

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    extraction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    result_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_confidence: Mapped[float | None] = mapped_column(Float)
    detected_language: Mapped[str | None] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_domain(self) -> ExtractionResult:
        return ExtractionResult(
            id=str(self.id),
            document_id=self.document_id,
            tenant_id=self.tenant_id,
            extraction_type=ExtractionType(self.extraction_type),
            result_data=self.result_data,
            model_version=self.model_version,
            processing_time_ms=self.processing_time_ms,
            mean_confidence=self.mean_confidence,
            detected_language=self.detected_language,
            created_at=self.created_at,
        )


# Database connection
_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url.get_secret_value(),
            echo=settings.debug,
        )
    return _engine


def get_session_factory():
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
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class ExtractionRepository:
    """Repository for extraction data."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_result(self, result: ExtractionResult) -> ExtractionResult:
        """Save extraction result."""
        from uuid import uuid4

        model = ExtractionResultModel(
            id=uuid4(),
            document_id=result.document_id,
            tenant_id=result.tenant_id,
            extraction_type=result.extraction_type.value,
            result_data=result.result_data,
            model_version=result.model_version,
            processing_time_ms=result.processing_time_ms,
            mean_confidence=result.mean_confidence,
            detected_language=result.detected_language,
            created_at=result.created_at or datetime.now(UTC),
        )
        self.session.add(model)
        await self.session.flush()
        return model.to_domain()

    async def get_by_document(self, document_id: str) -> ExtractionResult | None:
        """Get extraction result by document ID."""
        result = await self.session.execute(
            select(ExtractionResultModel).where(
                ExtractionResultModel.document_id == document_id
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None
