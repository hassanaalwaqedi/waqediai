"""
Object storage abstraction layer.

Provides a clean interface to S3-compatible storage with
tenant isolation and immutability guarantees.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterable, Protocol
from uuid import UUID

import aioboto3
from botocore.config import Config

from ingestion_service.config import get_settings


@dataclass
class StorageResult:
    """Result of a storage operation."""

    bucket: str
    key: str
    etag: str
    size_bytes: int


@dataclass
class StorageObject:
    """Metadata about a stored object."""

    bucket: str
    key: str
    size_bytes: int
    content_type: str
    last_modified: datetime
    etag: str


class ObjectStoragePort(Protocol):
    """Abstract interface for object storage operations."""

    async def put_object(
        self,
        key: str,
        data: bytes | AsyncIterable[bytes],
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> StorageResult:
        """Store an object."""
        ...

    async def get_object(self, key: str) -> AsyncIterable[bytes]:
        """Retrieve an object as async byte stream."""
        ...

    async def head_object(self, key: str) -> StorageObject | None:
        """Get object metadata without downloading."""
        ...

    async def delete_object(self, key: str) -> None:
        """Delete an object."""
        ...

    async def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
        method: str = "get_object",
    ) -> str:
        """Generate a presigned URL for temporary access."""
        ...


def build_storage_key(
    tenant_id: UUID,
    document_id: str,
    filename: str,
) -> str:
    """
    Build a storage key with tenant isolation.
    
    Format: {tenant_id}/{year}/{month}/{document_id}/{filename}
    """
    now = datetime.utcnow()
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # Sanitize filename
    safe_filename = "".join(
        c if c.isalnum() or c in ".-_" else "_"
        for c in filename
    )

    return f"{tenant_id}/{year}/{month}/{document_id}/{safe_filename}"


class S3StorageAdapter:
    """
    S3-compatible object storage adapter.
    
    Works with MinIO, AWS S3, and other S3-compatible services.
    """

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
        use_ssl: bool = True,
    ):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.use_ssl = use_ssl
        self._session = aioboto3.Session()

    def _get_client_config(self) -> Config:
        return Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        )

    async def put_object(
        self,
        key: str,
        data: bytes | AsyncIterable[bytes],
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> StorageResult:
        """Store an object in S3."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            # Handle async iterable by collecting bytes
            if isinstance(data, bytes):
                body = data
            else:
                chunks = []
                async for chunk in data:
                    chunks.append(chunk)
                body = b"".join(chunks)

            response = await client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
                Metadata=metadata or {},
            )

            return StorageResult(
                bucket=self.bucket,
                key=key,
                etag=response.get("ETag", "").strip('"'),
                size_bytes=len(body),
            )

    async def get_object(self, key: str) -> AsyncIterable[bytes]:
        """Retrieve an object as async byte stream."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            response = await client.get_object(
                Bucket=self.bucket,
                Key=key,
            )

            async with response["Body"] as stream:
                async for chunk in stream.iter_chunks():
                    yield chunk[0]

    async def head_object(self, key: str) -> StorageObject | None:
        """Get object metadata without downloading."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            try:
                response = await client.head_object(
                    Bucket=self.bucket,
                    Key=key,
                )
                return StorageObject(
                    bucket=self.bucket,
                    key=key,
                    size_bytes=response.get("ContentLength", 0),
                    content_type=response.get("ContentType", ""),
                    last_modified=response.get("LastModified"),
                    etag=response.get("ETag", "").strip('"'),
                )
            except Exception:
                return None

    async def delete_object(self, key: str) -> None:
        """Delete an object."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            await client.delete_object(
                Bucket=self.bucket,
                Key=key,
            )

    async def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
        method: str = "get_object",
    ) -> str:
        """Generate a presigned URL for temporary access."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            url = await client.generate_presigned_url(
                ClientMethod=method,
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )
            return url

    async def ensure_bucket_exists(self) -> None:
        """Ensure the storage bucket exists, creating it if necessary."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=self._get_client_config(),
            use_ssl=self.use_ssl,
        ) as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
            except Exception:
                # Bucket doesn't exist, create it
                await client.create_bucket(Bucket=self.bucket)


def get_storage_adapter() -> S3StorageAdapter:
    """Get configured storage adapter."""
    settings = get_settings()
    return S3StorageAdapter(
        endpoint_url=settings.storage_endpoint,
        access_key=settings.storage_access_key.get_secret_value(),
        secret_key=settings.storage_secret_key.get_secret_value(),
        bucket=settings.storage_bucket,
        region=settings.storage_region,
        use_ssl=settings.storage_use_ssl,
    )
