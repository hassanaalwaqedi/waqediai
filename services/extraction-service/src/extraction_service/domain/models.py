"""
Domain models for text extraction.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class ExtractionType(str, Enum):
    """Type of extraction."""
    OCR = "ocr"
    STT = "stt"


class JobStatus(str, Enum):
    """Extraction job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BoundingBox:
    """Bounding box for text location."""
    x: int
    y: int
    width: int
    height: int

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}


@dataclass
class TextBlock:
    """A block of extracted text with metadata."""
    text: str
    confidence: float
    bounding_box: BoundingBox
    block_type: str = "word"  # word, line, paragraph

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box.to_dict(),
            "block_type": self.block_type,
        }


@dataclass
class OCRPageResult:
    """OCR result for a single page."""
    page_number: int
    blocks: list[TextBlock]
    full_text: str
    mean_confidence: float
    detected_language: str | None = None

    def to_dict(self) -> dict:
        return {
            "page_number": self.page_number,
            "blocks": [b.to_dict() for b in self.blocks],
            "full_text": self.full_text,
            "mean_confidence": self.mean_confidence,
            "detected_language": self.detected_language,
        }


@dataclass
class OCRResult:
    """Complete OCR result for a document."""
    document_id: str
    pages: list[OCRPageResult]
    total_pages: int
    processing_time_ms: int
    model_version: str
    mean_confidence: float = 0.0

    def __post_init__(self):
        if self.pages and not self.mean_confidence:
            self.mean_confidence = sum(p.mean_confidence for p in self.pages) / len(self.pages)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.full_text for p in self.pages)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "pages": [p.to_dict() for p in self.pages],
            "total_pages": self.total_pages,
            "processing_time_ms": self.processing_time_ms,
            "model_version": self.model_version,
            "mean_confidence": self.mean_confidence,
            "full_text": self.full_text,
        }


@dataclass
class TranscriptSegment:
    """A segment of transcribed audio."""
    text: str
    start_time: float  # seconds
    end_time: float
    confidence: float | None = None
    speaker_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "confidence": self.confidence,
            "speaker_id": self.speaker_id,
        }


@dataclass
class STTResult:
    """Complete speech-to-text result."""
    document_id: str
    segments: list[TranscriptSegment]
    duration_seconds: float
    detected_language: str
    processing_time_ms: int
    model_version: str
    mean_confidence: float | None = None

    @property
    def full_text(self) -> str:
        return " ".join(s.text for s in self.segments)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "segments": [s.to_dict() for s in self.segments],
            "full_text": self.full_text,
            "duration_seconds": self.duration_seconds,
            "detected_language": self.detected_language,
            "processing_time_ms": self.processing_time_ms,
            "model_version": self.model_version,
            "mean_confidence": self.mean_confidence,
        }


@dataclass
class ExtractionJob:
    """An extraction job to process."""
    id: str
    document_id: str
    tenant_id: UUID
    job_type: ExtractionType
    status: JobStatus = JobStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    error_message: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def can_retry(self) -> bool:
        return self.attempts < self.max_attempts


@dataclass
class ExtractionResult:
    """Stored extraction result."""
    id: str
    document_id: str
    tenant_id: UUID
    extraction_type: ExtractionType
    result_data: dict  # Serialized OCRResult or STTResult
    model_version: str
    processing_time_ms: int
    mean_confidence: float | None
    detected_language: str | None
    created_at: datetime | None = None


@dataclass
class LanguageResult:
    """Language detection result."""
    language: str  # ISO 639-1
    confidence: float
    script: str  # latin, arabic, etc.
