"""
Repository for document data access.
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_service.adapters.database import DocumentModel
from ingestion_service.domain.models import Document, DocumentStatus


class DocumentRepository:
    """Repository for document data access with tenant isolation."""

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    async def create(self, document: Document) -> Document:
        """Create a new document record."""
        model = DocumentModel.from_domain(document)
        self.session.add(model)
        await self.session.flush()
        return model.to_domain()

    async def get_by_id(self, document_id: str) -> Document | None:
        """Get document by ID within tenant scope."""
        result = await self.session.execute(
            select(DocumentModel).where(
                and_(
                    DocumentModel.id == document_id,
                    DocumentModel.tenant_id == self.tenant_id,
                    DocumentModel.deleted_at.is_(None),
                )
            )
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def update_status(
        self,
        document_id: str,
        new_status: DocumentStatus,
        timestamp_field: str | None = None,
    ) -> None:
        """Update document status atomically."""
        values = {"status": new_status.value}

        if timestamp_field:
            values[timestamp_field] = datetime.now(UTC)

        await self.session.execute(
            update(DocumentModel)
            .where(
                and_(
                    DocumentModel.id == document_id,
                    DocumentModel.tenant_id == self.tenant_id,
                )
            )
            .values(**values)
        )

    async def soft_delete(self, document_id: str) -> None:
        """Mark document as deleted."""
        await self.session.execute(
            update(DocumentModel)
            .where(
                and_(
                    DocumentModel.id == document_id,
                    DocumentModel.tenant_id == self.tenant_id,
                )
            )
            .values(
                status=DocumentStatus.DELETED.value,
                deleted_at=datetime.now(UTC),
            )
        )

    async def list_documents(
        self,
        limit: int = 20,
        cursor: str | None = None,
        status: DocumentStatus | None = None,
        file_category: str | None = None,
        collection_id: UUID | None = None,
    ) -> tuple[Sequence[Document], str | None]:
        """List documents with cursor-based pagination."""
        conditions = [
            DocumentModel.tenant_id == self.tenant_id,
            DocumentModel.deleted_at.is_(None),
        ]

        if status:
            conditions.append(DocumentModel.status == status.value)
        if file_category:
            conditions.append(DocumentModel.file_category == file_category)
        if collection_id:
            conditions.append(DocumentModel.collection_id == collection_id)
        if cursor:
            conditions.append(DocumentModel.id < cursor)

        query = (
            select(DocumentModel)
            .where(and_(*conditions))
            .order_by(DocumentModel.id.desc())
            .limit(limit + 1)  # Fetch one extra to check for more
        )

        result = await self.session.execute(query)
        models = list(result.scalars())

        # Determine next cursor
        has_more = len(models) > limit
        if has_more:
            models = models[:limit]

        documents = [m.to_domain() for m in models]
        next_cursor = documents[-1].id if has_more else None

        return documents, next_cursor

    async def count_by_tenant(self) -> int:
        """Count documents for tenant (for quota checking)."""
        result = await self.session.execute(
            select(func.count(DocumentModel.id)).where(
                and_(
                    DocumentModel.tenant_id == self.tenant_id,
                    DocumentModel.deleted_at.is_(None),
                )
            )
        )
        return result.scalar() or 0

    async def sum_size_by_tenant(self) -> int:
        """Sum storage used by tenant (for quota checking)."""
        result = await self.session.execute(
            select(func.sum(DocumentModel.size_bytes)).where(
                and_(
                    DocumentModel.tenant_id == self.tenant_id,
                    DocumentModel.deleted_at.is_(None),
                )
            )
        )
        return result.scalar() or 0
