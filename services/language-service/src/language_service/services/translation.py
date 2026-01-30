"""
Translation service.

Configurable translation with multiple engine support.
"""

import logging
from datetime import datetime, timezone
from typing import Protocol

from language_service.domain import TranslationResult, TranslationConfig, TranslationStrategy
from language_service.config import get_settings

logger = logging.getLogger(__name__)


class TranslationEngineProtocol(Protocol):
    """Abstract interface for translation engines."""

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult: ...


class MockTranslationEngine:
    """
    Mock translation engine for development.
    
    In production, replace with Google/Azure/DeepL adapter.
    """

    def __init__(self, engine_name: str = "mock"):
        self.engine_name = engine_name
        self.version = "v1.0.0"

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """Mock translation - returns placeholder."""
        # In production, call actual translation API
        translated = f"[{target_lang}] {text}"

        return TranslationResult(
            source_language=source_lang,
            target_language=target_lang,
            source_text=text,
            translated_text=translated,
            engine=self.engine_name,
            engine_version=self.version,
            confidence=None,
            timestamp=datetime.now(timezone.utc),
        )


class TranslationService:
    """
    Translation service with configurable strategy.
    
    Supports:
    - Native: Process in original language
    - Canonical: Translate everything to one language
    - Hybrid: On-demand translation
    """

    def __init__(self, engine: TranslationEngineProtocol | None = None):
        self.engine = engine or MockTranslationEngine()

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationResult:
        """Translate text between languages."""
        if source_lang == target_lang:
            return TranslationResult(
                source_language=source_lang,
                target_language=target_lang,
                source_text=text,
                translated_text=text,
                engine="passthrough",
                engine_version="1.0",
                timestamp=datetime.now(timezone.utc),
            )

        return await self.engine.translate(text, source_lang, target_lang)

    def should_translate(
        self,
        config: TranslationConfig,
        detected_language: str,
    ) -> bool:
        """Determine if translation should occur based on config."""
        if config.strategy == TranslationStrategy.NATIVE:
            return False

        if config.strategy == TranslationStrategy.CANONICAL:
            return detected_language != config.canonical_language

        # Hybrid - translate on ingest if configured
        if config.strategy == TranslationStrategy.HYBRID:
            return config.translate_on_ingest

        return False


def get_translation_service() -> TranslationService:
    """Get translation service instance."""
    return TranslationService()
