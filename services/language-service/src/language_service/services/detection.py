"""
Language detection service.

Multi-granularity language detection with confidence scoring.
"""

import logging
from typing import Protocol

from language_service.domain import LanguageDetectionResult, Script
from language_service.config import get_settings

logger = logging.getLogger(__name__)


class LanguageDetectorProtocol(Protocol):
    """Abstract interface for language detection."""

    def detect(self, text: str) -> LanguageDetectionResult: ...
    def detect_batch(self, texts: list[str]) -> list[LanguageDetectionResult]: ...


class HybridLanguageDetector:
    """
    Hybrid language detector using langdetect + fasttext.
    
    - langdetect for short text (< 50 chars)
    - fasttext for longer content (higher accuracy)
    """

    def __init__(self):
        self._fasttext_model = None

    def _get_fasttext_model(self):
        """Lazy load fasttext model."""
        if self._fasttext_model is None:
            try:
                import fasttext
                # Will download model on first use
                self._fasttext_model = fasttext.load_model('lid.176.ftz')
            except Exception as e:
                logger.warning(f"Fasttext model not available: {e}")
                self._fasttext_model = None
        return self._fasttext_model

    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Detect language of text.
        
        Uses langdetect for short text, fasttext for longer.
        """
        if not text or len(text.strip()) < 10:
            return LanguageDetectionResult(
                primary_language="unknown",
                confidence=0.0,
                script=Script.UNKNOWN,
            )

        # Determine script first
        script = self._detect_script(text)

        # Use langdetect for short text
        if len(text) < 50:
            return self._detect_langdetect(text, script)

        # Try fasttext for longer text
        fasttext_model = self._get_fasttext_model()
        if fasttext_model:
            return self._detect_fasttext(text, script)

        # Fallback to langdetect
        return self._detect_langdetect(text, script)

    def _detect_langdetect(self, text: str, script: Script) -> LanguageDetectionResult:
        """Detect using langdetect library."""
        try:
            from langdetect import detect_langs

            results = detect_langs(text)
            if results:
                primary = results[0]
                secondary = [(r.lang, r.prob) for r in results[1:3]]

                return LanguageDetectionResult(
                    primary_language=primary.lang,
                    confidence=primary.prob,
                    secondary_languages=secondary,
                    is_mixed=len(results) > 1 and results[1].prob > 0.2,
                    script=script,
                )
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")

        return LanguageDetectionResult(
            primary_language="unknown",
            confidence=0.0,
            script=script,
        )

    def _detect_fasttext(self, text: str, script: Script) -> LanguageDetectionResult:
        """Detect using fasttext model."""
        try:
            model = self._get_fasttext_model()
            if not model:
                return self._detect_langdetect(text, script)

            # Clean text for fasttext
            clean_text = text.replace('\n', ' ')[:1000]
            predictions = model.predict(clean_text, k=3)

            labels, scores = predictions
            primary_lang = labels[0].replace('__label__', '')
            primary_score = float(scores[0])

            secondary = [
                (labels[i].replace('__label__', ''), float(scores[i]))
                for i in range(1, min(3, len(labels)))
            ]

            return LanguageDetectionResult(
                primary_language=primary_lang,
                confidence=primary_score,
                secondary_languages=secondary,
                is_mixed=len(secondary) > 0 and secondary[0][1] > 0.2,
                script=script,
            )
        except Exception as e:
            logger.warning(f"Fasttext detection failed: {e}")
            return self._detect_langdetect(text, script)

    def _detect_script(self, text: str) -> Script:
        """Detect primary script of text."""
        sample = text[:500]

        arabic_chars = sum(1 for c in sample if '\u0600' <= c <= '\u06FF')
        latin_chars = sum(1 for c in sample if c.isalpha() and c.isascii())
        total_alpha = arabic_chars + latin_chars

        if total_alpha == 0:
            return Script.UNKNOWN
        if arabic_chars > latin_chars * 2:
            return Script.ARABIC
        if latin_chars > arabic_chars * 2:
            return Script.LATIN
        return Script.MIXED

    def detect_batch(self, texts: list[str]) -> list[LanguageDetectionResult]:
        """Detect language for multiple texts."""
        return [self.detect(text) for text in texts]


def get_language_detector() -> HybridLanguageDetector:
    """Get language detector instance."""
    return HybridLanguageDetector()
