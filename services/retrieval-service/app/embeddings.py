"""
Embedding adapter with pluggable providers.

Abstracts embedding generation for model-agnostic design.
"""

from typing import Protocol

from app.config import get_settings
from app.logging import get_logger

logger = get_logger(__name__)


class EmbeddingProvider(Protocol):
    """Abstract interface for embedding providers."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        ...

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        ...

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        ...


class SentenceTransformerProvider:
    """
    Sentence-Transformers embedding provider.

    Uses local models for privacy and performance.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._dimension: int | None = None

    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {self.model_name} (dim={self._dimension})")
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        model = self._get_model()
        embedding = model.encode(query, convert_to_numpy=True)
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        if self._dimension is None:
            self._get_model()
        return self._dimension


class EmbeddingService:
    """
    Service for generating embeddings with configurable provider.
    """

    def __init__(self, provider: EmbeddingProvider | None = None):
        if provider is None:
            settings = get_settings()
            if settings.embedding_provider == "sentence-transformers":
                provider = SentenceTransformerProvider(settings.embedding_model)
            else:
                raise ValueError(f"Unknown provider: {settings.embedding_provider}")
        self.provider = provider

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        return self.provider.embed_texts(texts)

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for query."""
        return self.provider.embed_query(query)

    @property
    def dimension(self) -> int:
        return self.provider.dimension


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
