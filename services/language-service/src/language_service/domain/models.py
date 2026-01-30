"""
Domain models for language processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class TranslationStrategy(str, Enum):
    """Translation strategy types."""
    NATIVE = "native"      # Process in original language
    CANONICAL = "canonical"  # Translate to single language
    HYBRID = "hybrid"       # Translate on-demand


class Script(str, Enum):
    """Script types."""
    LATIN = "latin"
    ARABIC = "arabic"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class LanguageDetectionResult:
    """Result of language detection."""
    primary_language: str  # ISO 639-1
    confidence: float
    secondary_languages: list[tuple[str, float]] = field(default_factory=list)
    is_mixed: bool = False
    script: Script = Script.UNKNOWN

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.8

    @property
    def needs_review(self) -> bool:
        return self.confidence < 0.5


@dataclass
class NormalizationChange:
    """Record of a single normalization change."""
    position: int
    original: str
    replacement: str
    rule: str


@dataclass
class NormalizationRecord:
    """Complete normalization record for traceability."""
    original_text: str
    normalized_text: str
    changes: list[NormalizationChange]
    version: str
    language: str

    @property
    def change_count(self) -> int:
        return len(self.changes)


@dataclass
class TranslationResult:
    """Result of text translation."""
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    engine: str
    engine_version: str
    confidence: float | None = None
    timestamp: datetime | None = None


@dataclass
class LinguisticArtifact:
    """Complete linguistic artifact with metadata."""
    id: str
    document_id: str
    tenant_id: UUID

    # Text content
    original_text: str
    normalized_text: str
    translated_text: str | None = None

    # Language info
    language_code: str = "unknown"
    detection_confidence: float = 0.0
    script: Script = Script.UNKNOWN

    # Normalization
    normalization_version: str = ""
    normalization_changes: list[dict] = field(default_factory=list)

    # Translation
    is_translated: bool = False
    translation_engine: str | None = None
    translation_source_id: str | None = None

    # Position
    page_number: int | None = None
    segment_index: int = 0

    # Timestamps
    created_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "tenant_id": str(self.tenant_id),
            "original_text": self.original_text,
            "normalized_text": self.normalized_text,
            "translated_text": self.translated_text,
            "language_code": self.language_code,
            "detection_confidence": self.detection_confidence,
            "script": self.script.value,
            "normalization_version": self.normalization_version,
            "is_translated": self.is_translated,
            "translation_engine": self.translation_engine,
            "page_number": self.page_number,
            "segment_index": self.segment_index,
        }


@dataclass
class TranslationConfig:
    """Per-tenant translation configuration."""
    strategy: TranslationStrategy
    canonical_language: str = "en"
    translate_on_ingest: bool = False
    preserve_original: bool = True  # Always True
    translation_engine: str = "google"


@dataclass
class ProcessingJob:
    """Language processing job."""
    id: str
    document_id: str
    tenant_id: UUID
    extraction_id: str
    status: str = "pending"  # pending, processing, completed, failed
    config: TranslationConfig | None = None
    created_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
