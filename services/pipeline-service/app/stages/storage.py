"""
Qdrant storage stage.

Stores embedded chunks in Qdrant with tenant isolation.
"""

import logging
from datetime import UTC, datetime

from app.config import get_settings
from app.models import EmbeddedChunk
from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Qdrant vector store with tenant isolation.

    Uses a shared collection with mandatory tenant_id filtering.
    """

    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = f"{settings.qdrant_collection_prefix}_knowledge"
        self.dimension = settings.embedding_dimension
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the collection exists with proper configuration."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=models.Distance.COSINE,
                    ),
                )

                # Create indexes for filtering
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="tenant_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="language",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )

                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Could not ensure collection: {e}")

    def store(self, chunks: list[EmbeddedChunk]) -> int:
        """
        Store embedded chunks in Qdrant.

        Returns number of vectors stored.
        """
        if not chunks:
            return 0

        points = []
        for chunk in chunks:
            point_id = f"{chunk.tenant_id}_{chunk.chunk_id}"

            points.append(models.PointStruct(
                id=point_id,
                vector=chunk.vector,
                payload={
                    "tenant_id": str(chunk.tenant_id),
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "language": chunk.language,
                    "embedding_model": chunk.embedding_model,
                    "embedding_version": chunk.embedding_version,
                    "source_type": chunk.metadata.get("source_type", "document"),
                    "page_number": chunk.metadata.get("page_number"),
                    "chunk_index": chunk.metadata.get("chunk_index"),
                    "token_count": chunk.metadata.get("token_count"),
                    "ingestion_timestamp": datetime.now(UTC).isoformat(),
                },
            ))

        # Upsert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
            )

        logger.info(
            f"Stored {len(points)} vectors in Qdrant "
            f"(collection: {self.collection_name})"
        )
        return len(points)

    def delete_document(self, tenant_id: str, document_id: str) -> int:
        """Delete all vectors for a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="tenant_id",
                            match=models.MatchValue(value=tenant_id),
                        ),
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        ),
                    ]
                )
            ),
        )
        logger.info(f"Deleted vectors for document {document_id}")
        return 0

    def health_check(self) -> bool:
        """Check Qdrant connectivity."""
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


def get_vector_store() -> VectorStore:
    """Get vector store instance."""
    return VectorStore()
