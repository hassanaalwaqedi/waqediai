"""
Language processing orchestrator.

Coordinates detection, normalization, and translation.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from language_service.domain import (
    LinguisticArtifact,
    TranslationConfig,
    TranslationStrategy,
)
from language_service.services.detection import get_language_detector
from language_service.services.normalization import get_text_normalizer
from language_service.services.translation import get_translation_service
from language_service.config import get_settings

logger = logging.getLogger(__name__)


class LanguageProcessor:
    """
    Orchestrates the language processing pipeline.
    
    Detection → Normalization → Translation (optional)
    """

    def __init__(self):
        self.detector = get_language_detector()
        self.normalizer = get_text_normalizer()
        self.translator = get_translation_service()
        settings = get_settings()
        self.normalization_version = settings.normalization_version

    async def process(
        self,
        document_id: str,
        tenant_id: UUID,
        text: str,
        page_number: int | None = None,
        segment_index: int = 0,
        config: TranslationConfig | None = None,
    ) -> LinguisticArtifact:
        """
        Process text through the full language pipeline.
        
        Args:
            document_id: Parent document ID.
            tenant_id: Tenant context.
            text: Raw text to process.
            page_number: Optional page reference.
            segment_index: Position in document.
            config: Translation configuration.
            
        Returns:
            Complete LinguisticArtifact.
        """
        settings = get_settings()

        # Step 1: Language detection
        detection = self.detector.detect(text)
        detected_lang = detection.primary_language

        logger.info(
            f"Language detected: {detected_lang} ({detection.confidence:.2f})",
            extra={"document_id": document_id, "language": detected_lang},
        )

        # Step 2: Text normalization
        norm_record = self.normalizer.normalize(text, detected_lang)

        logger.info(
            f"Text normalized: {norm_record.change_count} changes",
            extra={"document_id": document_id, "changes": norm_record.change_count},
        )

        # Step 3: Translation (if configured)
        translated_text = None
        translation_engine = None

        if config is None:
            config = TranslationConfig(
                strategy=TranslationStrategy(settings.default_translation_strategy),
                canonical_language=settings.canonical_language,
            )

        if self.translator.should_translate(config, detected_lang):
            result = await self.translator.translate(
                norm_record.normalized_text,
                detected_lang,
                config.canonical_language,
            )
            translated_text = result.translated_text
            translation_engine = result.engine

            logger.info(
                f"Text translated: {detected_lang} → {config.canonical_language}",
                extra={"document_id": document_id},
            )

        # Build artifact
        artifact = LinguisticArtifact(
            id=f"lng_{uuid4().hex[:16]}",
            document_id=document_id,
            tenant_id=tenant_id,
            original_text=text,
            normalized_text=norm_record.normalized_text,
            translated_text=translated_text,
            language_code=detected_lang,
            detection_confidence=detection.confidence,
            script=detection.script,
            normalization_version=self.normalization_version,
            normalization_changes=[
                {"rule": c.rule, "position": c.position}
                for c in norm_record.changes
            ],
            is_translated=translated_text is not None,
            translation_engine=translation_engine,
            page_number=page_number,
            segment_index=segment_index,
            created_at=datetime.now(timezone.utc),
        )

        return artifact

    async def process_document(
        self,
        document_id: str,
        tenant_id: UUID,
        segments: list[dict],
        config: TranslationConfig | None = None,
    ) -> list[LinguisticArtifact]:
        """
        Process all segments of a document.
        
        Args:
            document_id: Parent document ID.
            tenant_id: Tenant context.
            segments: List of {"text": str, "page": int, "index": int}.
            config: Translation configuration.
            
        Returns:
            List of LinguisticArtifacts.
        """
        artifacts = []

        for seg in segments:
            artifact = await self.process(
                document_id=document_id,
                tenant_id=tenant_id,
                text=seg["text"],
                page_number=seg.get("page"),
                segment_index=seg.get("index", 0),
                config=config,
            )
            artifacts.append(artifact)

        return artifacts


def get_language_processor() -> LanguageProcessor:
    """Get language processor instance."""
    return LanguageProcessor()
