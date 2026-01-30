"""
Upload service.

Handles file upload validation, storage, and metadata creation.
"""

import hashlib
import logging
from datetime import datetime, timezone
from uuid import UUID

from ingestion_service.adapters import (
    get_session,
    DocumentRepository,
    get_storage_adapter,
    build_storage_key,
)
from ingestion_service.domain import (
    Document,
    DocumentStatus,
    FileCategory,
    generate_document_id,
    get_file_category,
    is_allowed_content_type,
    get_max_size_bytes,
    document_uploaded_event,
    document_validated_event,
)
from ingestion_service.services.events import get_event_publisher
from ingestion_service.config import get_settings

logger = logging.getLogger(__name__)


class UploadError(Exception):
    """Base class for upload errors."""

    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class UnsupportedMediaType(UploadError):
    """File type not supported."""

    def __init__(self, content_type: str):
        super().__init__(
            f"Content type '{content_type}' is not supported",
            "UNSUPPORTED_MEDIA_TYPE",
        )


class FileTooLarge(UploadError):
    """File exceeds size limit."""

    def __init__(self, size_bytes: int, max_bytes: int):
        super().__init__(
            f"File size {size_bytes} exceeds limit of {max_bytes} bytes",
            "FILE_TOO_LARGE",
        )


class QuotaExceeded(UploadError):
    """Tenant storage quota exceeded."""

    def __init__(self, used: int, limit: int):
        super().__init__(
            f"Storage quota exceeded: {used} / {limit} bytes",
            "QUOTA_EXCEEDED",
        )


class UploadService:
    """
    Service for handling file uploads.
    
    Responsible for:
    - Validating file type and size
    - Storing file in object storage
    - Creating metadata record
    - Publishing upload event
    """

    async def upload(
        self,
        tenant_id: UUID,
        user_id: UUID,
        filename: str,
        content_type: str,
        file_data: bytes,
        department_id: UUID | None = None,
        collection_id: UUID | None = None,
        correlation_id: str = "",
    ) -> Document:
        """
        Process a file upload.
        
        Args:
            tenant_id: Tenant context.
            user_id: Uploading user.
            filename: Original filename.
            content_type: MIME type.
            file_data: File content.
            department_id: Optional department scope.
            collection_id: Optional collection.
            correlation_id: Request correlation ID.
            
        Returns:
            Created document record.
            
        Raises:
            UnsupportedMediaType: If file type not allowed.
            FileTooLarge: If file exceeds size limit.
            QuotaExceeded: If tenant quota exceeded.
        """
        settings = get_settings()

        # Validate content type
        if not is_allowed_content_type(content_type):
            raise UnsupportedMediaType(content_type)

        # Validate size
        size_bytes = len(file_data)
        max_size = get_max_size_bytes(content_type)
        if size_bytes > max_size:
            raise FileTooLarge(size_bytes, max_size)

        # Generate document ID
        document_id = generate_document_id()

        # Compute checksum
        checksum = hashlib.sha256(file_data).hexdigest()

        # Build storage key
        storage_key = build_storage_key(tenant_id, document_id, filename)

        # Get file category
        file_category = get_file_category(content_type)

        async with get_session() as session:
            repo = DocumentRepository(session, tenant_id)

            # TODO: Check tenant quota
            # current_usage = await repo.sum_size_by_tenant()
            # if current_usage + size_bytes > tenant_quota:
            #     raise QuotaExceeded(current_usage, tenant_quota)

            # Store file in object storage
            storage = get_storage_adapter()
            storage_result = await storage.put_object(
                key=storage_key,
                data=file_data,
                content_type=content_type,
                metadata={
                    "document_id": document_id,
                    "tenant_id": str(tenant_id),
                    "uploaded_by": str(user_id),
                    "checksum": checksum,
                },
            )

            # Create document record
            document = Document(
                id=document_id,
                tenant_id=tenant_id,
                uploaded_by=user_id,
                department_id=department_id,
                collection_id=collection_id,
                filename=filename,
                content_type=content_type,
                size_bytes=size_bytes,
                checksum_sha256=checksum,
                file_category=file_category,
                status=DocumentStatus.UPLOADED,
                storage_bucket=settings.storage_bucket,
                storage_key=storage_key,
                uploaded_at=datetime.now(timezone.utc),
            )

            document = await repo.create(document)

            logger.info(
                f"Document uploaded: {document_id}",
                extra={
                    "document_id": document_id,
                    "tenant_id": str(tenant_id),
                    "filename": filename,
                    "size_bytes": size_bytes,
                },
            )

        # Publish upload event
        try:
            publisher = await get_event_publisher()
            event = document_uploaded_event(
                document_id=document_id,
                tenant_id=str(tenant_id),
                correlation_id=correlation_id,
                file_category=file_category,
                content_type=content_type,
                size_bytes=size_bytes,
            )
            await publisher.publish(event)
        except Exception as e:
            # Log but don't fail the upload
            logger.warning(f"Failed to publish upload event: {e}")

        return document

    async def validate_and_queue(
        self,
        document_id: str,
        tenant_id: UUID,
        correlation_id: str = "",
    ) -> Document:
        """
        Validate document and queue for processing.
        
        This is typically called after async validation checks.
        """
        async with get_session() as session:
            repo = DocumentRepository(session, tenant_id)
            document = await repo.get_by_id(document_id)

            if not document:
                raise ValueError(f"Document {document_id} not found")

            # Transition to VALIDATED then QUEUED
            document.transition_to(DocumentStatus.VALIDATED)
            await repo.update_status(
                document_id,
                DocumentStatus.VALIDATED,
                "validated_at",
            )

            document.transition_to(DocumentStatus.QUEUED)
            await repo.update_status(document_id, DocumentStatus.QUEUED)

        # Publish events
        try:
            publisher = await get_event_publisher()
            event = document_validated_event(
                document_id=document_id,
                tenant_id=str(tenant_id),
                correlation_id=correlation_id,
            )
            await publisher.publish(event)
        except Exception as e:
            logger.warning(f"Failed to publish validated event: {e}")

        return document
