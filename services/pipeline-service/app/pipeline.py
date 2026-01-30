"""
Pipeline orchestrator.

Coordinates the full document-to-embedding pipeline.
"""

import logging
import time
from typing import Optional

from app.models import (
    DocumentInput,
    PipelineResult,
    ProcessingStatus,
)
from app.stages import (
    get_extractor,
    get_normalizer,
    get_chunker,
    get_embedder,
    get_vector_store,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Document ingestion pipeline orchestrator.
    
    Coordinates: Extract → Normalize → Chunk → Embed → Store
    """

    def __init__(self):
        self.extractor = get_extractor()
        self.normalizer = get_normalizer()
        self.chunker = get_chunker()
        self.embedder = get_embedder()
        self.store = get_vector_store()

    def process(self, document: DocumentInput) -> PipelineResult:
        """
        Process a document through the full pipeline.
        
        Each stage is executed with error handling to prevent
        cascading failures.
        """
        start_time = time.time()
        status = ProcessingStatus.PENDING

        try:
            # Stage 1: Extraction
            logger.info(f"[{document.document_id}] Starting extraction...")
            status = ProcessingStatus.EXTRACTING
            extracted = self.extractor.extract(document)

            logger.info(
                f"[{document.document_id}] Extracted {len(extracted.pages)} pages, "
                f"type={extracted.document_type.value}, lang={extracted.source_language}"
            )

            # Stage 2: Normalization
            logger.info(f"[{document.document_id}] Starting normalization...")
            status = ProcessingStatus.NORMALIZING
            normalized = self.normalizer.normalize(extracted)

            logger.info(
                f"[{document.document_id}] Normalized: "
                f"{normalized.original_length} → {normalized.normalized_length} chars"
            )

            # Stage 3: Chunking
            logger.info(f"[{document.document_id}] Starting chunking...")
            status = ProcessingStatus.CHUNKING
            chunks = self.chunker.chunk(normalized)

            logger.info(f"[{document.document_id}] Created {len(chunks)} chunks")

            # Stage 4: Embedding
            logger.info(f"[{document.document_id}] Starting embedding...")
            status = ProcessingStatus.EMBEDDING
            embedded = self.embedder.embed_chunks(chunks)

            logger.info(f"[{document.document_id}] Generated {len(embedded)} embeddings")

            # Stage 5: Storage
            logger.info(f"[{document.document_id}] Storing in Qdrant...")
            status = ProcessingStatus.STORING

            # Add source type to metadata
            for chunk in embedded:
                chunk.metadata["source_type"] = extracted.document_type.value

            vectors_stored = self.store.store(embedded)

            # Success
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"[{document.document_id}] Pipeline complete: "
                f"{vectors_stored} vectors in {processing_time}ms"
            )

            return PipelineResult(
                document_id=document.document_id,
                tenant_id=document.tenant_id,
                status=ProcessingStatus.COMPLETED,
                chunks_created=len(chunks),
                vectors_stored=vectors_stored,
                document_type=extracted.document_type,
                language=extracted.source_language,
                processing_time_ms=processing_time,
                metadata={
                    "extraction_confidence": extracted.extraction_confidence,
                    "embedding_model": self.embedder.model_name,
                    "embedding_version": self.embedder.version,
                },
            )

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.exception(f"[{document.document_id}] Pipeline failed at {status.value}")

            return PipelineResult(
                document_id=document.document_id,
                tenant_id=document.tenant_id,
                status=ProcessingStatus.FAILED,
                chunks_created=0,
                vectors_stored=0,
                document_type=None,
                language="unknown",
                processing_time_ms=processing_time,
                error=str(e),
            )

    def delete_document(self, tenant_id: str, document_id: str) -> bool:
        """Remove a document from the vector store."""
        try:
            self.store.delete_document(tenant_id, document_id)
            logger.info(f"Deleted document {document_id} from vector store")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False


def get_pipeline() -> Pipeline:
    """Get pipeline instance."""
    return Pipeline()
