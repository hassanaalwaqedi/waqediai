"""
Hybrid retrieval module.

Multi-stage retrieval with vector similarity and metadata filtering.
"""

import logging

from app.config import get_settings
from app.models import EnrichedQuery, RAGQuery, RetrievedChunk
from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Multi-stage retrieval system.

    Combines:
    1. Vector similarity search
    2. Metadata filtering (tenant, language)
    3. Score thresholding
    """

    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection = settings.qdrant_collection
        self.min_score = settings.min_relevance_score
        self._embedder = None

    def _get_embedder(self):
        """Lazy load embedding model."""
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            settings = get_settings()
            self._embedder = SentenceTransformer(settings.embedding_model)
        return self._embedder

    def retrieve(
        self,
        query: RAGQuery,
        enriched: EnrichedQuery,
    ) -> list[RetrievedChunk]:
        """
        Execute hybrid retrieval.
        """
        settings = get_settings()

        # Generate query embedding
        embedder = self._get_embedder()
        query_vector = embedder.encode(enriched.normalized_query).tolist()

        # Build filter conditions - always filter by tenant
        must_conditions = [
            models.FieldCondition(
                key="tenant_id",
                match=models.MatchValue(value=str(query.tenant_id)),
            )
        ]

        # Optional language filter
        if enriched.language:
            must_conditions.append(
                models.FieldCondition(
                    key="language",
                    match=models.MatchValue(value=enriched.language),
                )
            )

        # Apply custom filters
        if query.filters.get("document_id"):
            must_conditions.append(
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=query.filters["document_id"]),
                )
            )

        # Execute search
        try:
            results = self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                query_filter=models.Filter(must=must_conditions),
                limit=min(query.top_k * 2, settings.max_top_k),  # Over-fetch for reranking
                score_threshold=self.min_score,
                with_payload=True,
            )
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            return []

        # Convert to RetrievedChunk
        chunks = []
        for result in results:
            payload = result.payload
            chunks.append(RetrievedChunk(
                chunk_id=payload.get("chunk_id", ""),
                document_id=payload.get("document_id", ""),
                text=payload.get("text", ""),
                language=payload.get("language", "en"),
                score=result.score,
                metadata={
                    "page_number": payload.get("page_number"),
                    "chunk_index": payload.get("chunk_index"),
                    "embedding_model": payload.get("embedding_model"),
                    "ingestion_timestamp": payload.get("ingestion_timestamp"),
                },
            ))

        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks


def get_retriever() -> HybridRetriever:
    """Get retriever instance."""
    return HybridRetriever()
