"""
Embedding generation stage.

Converts text chunks into vector embeddings.
"""

import logging
from datetime import datetime, timezone

from app.models import TextChunk, EmbeddedChunk
from app.config import get_settings

logger = logging.getLogger(__name__)


class Embedder:
    """
    Text embedding generator.
    
    Uses sentence-transformers for consistent vector generation.
    """

    def __init__(self):
        settings = get_settings()
        self.model_name = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self.version = settings.embedding_version
        self._model = None

    def _get_model(self):
        """Lazy load embedding model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            actual_dim = self._model.get_sentence_embedding_dimension()
            logger.info(
                f"Loaded embedding model: {self.model_name} (dim={actual_dim})"
            )
        return self._model

    def embed_chunks(self, chunks: list[TextChunk]) -> list[EmbeddedChunk]:
        """
        Generate embeddings for all chunks.
        """
        if not chunks:
            return []

        model = self._get_model()
        texts = [chunk.text for chunk in chunks]

        # Batch embedding
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        embedded_chunks = []
        for chunk, vector in zip(chunks, embeddings):
            embedded_chunks.append(EmbeddedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                tenant_id=chunk.tenant_id,
                text=chunk.text,
                language=chunk.language,
                vector=vector.tolist(),
                embedding_model=self.model_name,
                embedding_version=self.version,
                metadata={
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "embedded_at": datetime.now(timezone.utc).isoformat(),
                },
            ))

        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return embedded_chunks


def get_embedder() -> Embedder:
    """Get embedder instance."""
    return Embedder()
