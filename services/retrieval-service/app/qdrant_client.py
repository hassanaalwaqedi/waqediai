"""
Qdrant vector database client.

Handles collection management, indexing, and similarity search.
"""

from dataclasses import dataclass
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import get_settings
from app.logging import get_logger
from app.embeddings import get_embedding_service

logger = get_logger(__name__)


@dataclass
class VectorPoint:
    """A point to store in Qdrant."""
    id: str
    vector: list[float]
    payload: dict


@dataclass
class SearchHit:
    """A search result from Qdrant."""
    chunk_id: str
    document_id: str
    text: str
    language: str
    score: float


class QdrantService:
    """
    Qdrant vector database service.
    
    Uses shared collection with tenant filtering for isolation.
    """

    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = f"{settings.qdrant_collection_prefix}_vectors"
        self.embedding_service = get_embedding_service()
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the collection exists."""
        settings = get_settings()
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )
            # Create payload index for tenant filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tenant_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def index_chunks(
        self,
        tenant_id: UUID,
        document_id: str,
        chunks: list[dict],
    ) -> int:
        """
        Index text chunks into Qdrant.
        
        Args:
            tenant_id: Tenant for isolation.
            document_id: Parent document ID.
            chunks: List of {"chunk_id", "text", "language"}.
            
        Returns:
            Number of chunks indexed.
        """
        if not chunks:
            return 0

        # Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        # Build points
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            point_id = f"{tenant_id}_{document_id}_{chunk['chunk_id']}"
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "tenant_id": str(tenant_id),
                    "document_id": document_id,
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "language": chunk.get("language", "en"),
                    "page_number": chunk.get("page_number"),
                },
            ))

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        logger.info(f"Indexed {len(points)} chunks for document {document_id}")
        return len(points)

    def search(
        self,
        tenant_id: UUID,
        query: str,
        top_k: int = 5,
        language: str | None = None,
        min_score: float | None = None,
    ) -> list[SearchHit]:
        """
        Perform semantic search within tenant scope.
        
        Args:
            tenant_id: Tenant for isolation (mandatory).
            query: Search query.
            top_k: Number of results.
            language: Optional language filter.
            min_score: Optional minimum score threshold.
            
        Returns:
            List of SearchHit results.
        """
        settings = get_settings()
        min_score = min_score or settings.min_score_threshold

        # Generate query embedding
        query_vector = self.embedding_service.embed_query(query)

        # Build filter - always include tenant_id
        must_conditions = [
            models.FieldCondition(
                key="tenant_id",
                match=models.MatchValue(value=str(tenant_id)),
            )
        ]

        if language:
            must_conditions.append(
                models.FieldCondition(
                    key="language",
                    match=models.MatchValue(value=language),
                )
            )

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=models.Filter(must=must_conditions),
            limit=top_k,
            score_threshold=min_score,
        )

        # Convert to SearchHit
        hits = []
        for result in results:
            hits.append(SearchHit(
                chunk_id=result.payload["chunk_id"],
                document_id=result.payload["document_id"],
                text=result.payload["text"],
                language=result.payload["language"],
                score=result.score,
            ))

        return hits

    def delete_document(self, tenant_id: UUID, document_id: str) -> int:
        """
        Delete all vectors for a document.
        
        Args:
            tenant_id: Tenant for isolation.
            document_id: Document to delete.
            
        Returns:
            Number of points deleted.
        """
        # Count before deletion
        count_before = self.client.count(
            collection_name=self.collection_name,
            count_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tenant_id",
                        match=models.MatchValue(value=str(tenant_id)),
                    ),
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    ),
                ]
            ),
        ).count

        # Delete
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="tenant_id",
                            match=models.MatchValue(value=str(tenant_id)),
                        ),
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id),
                        ),
                    ]
                )
            ),
        )

        logger.info(f"Deleted {count_before} vectors for document {document_id}")
        return count_before

    def health_check(self) -> bool:
        """Check Qdrant connectivity."""
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False


# Singleton
_qdrant_service: QdrantService | None = None


def get_qdrant_service() -> QdrantService:
    """Get or create Qdrant service."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service
