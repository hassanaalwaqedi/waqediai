"""
Data models for the ingestion pipeline.

Defines the data structures flowing through each pipeline stage.
"""

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID


class DocumentType(str, Enum):
    """Supported document types."""
    PDF_NATIVE = "pdf_native"
    PDF_SCANNED = "pdf_scanned"
    IMAGE = "image"
    TEXT = "text"


class ProcessingStatus(str, Enum):
    """Pipeline processing status."""
    PENDING = "pending"
    EXTRACTING = "extracting"
    NORMALIZING = "normalizing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DocumentInput:
    """Input document for pipeline processing."""
    tenant_id: UUID
    document_id: str
    filename: str
    content: bytes
    content_type: str
    metadata: dict = field(default_factory=dict)

    @property
    def extension(self) -> str:
        return "." + self.filename.rsplit(".", 1)[-1].lower()


@dataclass
class ExtractedText:
    """Text extracted from a document."""
    document_id: str
    tenant_id: UUID
    pages: list["PageText"]
    document_type: DocumentType
    source_language: str
    extraction_confidence: float
    extraction_time_ms: int


@dataclass
class PageText:
    """Text from a single page."""
    page_number: int
    text: str
    confidence: float
    bounding_boxes: list[dict] = field(default_factory=list)


@dataclass
class NormalizedText:
    """Normalized and cleaned text."""
    document_id: str
    tenant_id: UUID
    text: str
    language: str
    original_length: int
    normalized_length: int
    changes_applied: list[str]


@dataclass
class TextChunk:
    """A semantic chunk of text."""
    chunk_id: str
    document_id: str
    tenant_id: UUID
    text: str
    language: str
    page_number: int | None
    chunk_index: int
    token_count: int
    metadata: dict = field(default_factory=dict)


@dataclass
class EmbeddedChunk:
    """A chunk with its embedding vector."""
    chunk_id: str
    document_id: str
    tenant_id: UUID
    text: str
    language: str
    vector: list[float]
    embedding_model: str
    embedding_version: str
    metadata: dict = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Final result of pipeline processing."""
    document_id: str
    tenant_id: UUID
    status: ProcessingStatus
    chunks_created: int
    vectors_stored: int
    document_type: DocumentType
    language: str
    processing_time_ms: int
    error: str | None = None
    metadata: dict = field(default_factory=dict)
