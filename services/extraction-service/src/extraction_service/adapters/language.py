"""
Language detection utility.
"""

import logging

from extraction_service.domain import LanguageResult

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Detect language from text.

    Uses langdetect library for lightweight detection.
    """

    def detect(self, text: str) -> LanguageResult:
        """
        Detect language of text.

        Args:
            text: Text to analyze.

        Returns:
            Language detection result.
        """
        if not text or len(text.strip()) < 10:
            return LanguageResult(
                language="unknown",
                confidence=0.0,
                script="unknown",
            )

        try:
            from langdetect import detect_langs

            results = detect_langs(text)
            if results:
                top_result = results[0]
                language = top_result.lang
                confidence = top_result.prob

                # Determine script
                script = self._detect_script(text)

                return LanguageResult(
                    language=language,
                    confidence=confidence,
                    script=script,
                )
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")

        return LanguageResult(
            language="unknown",
            confidence=0.0,
            script="unknown",
        )

    def _detect_script(self, text: str) -> str:
        """Detect script type from text."""
        sample = text[:500]

        arabic_chars = sum(1 for c in sample if '\u0600' <= c <= '\u06FF')
        latin_chars = sum(1 for c in sample if c.isalpha() and c.isascii())

        if arabic_chars > latin_chars:
            return "arabic"
        return "latin"


def get_language_detector() -> LanguageDetector:
    """Get language detector instance."""
    return LanguageDetector()
