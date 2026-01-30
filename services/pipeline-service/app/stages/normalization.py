"""
Text normalization stage.

Cleans and normalizes extracted text for downstream processing.
"""

import logging
import re
import unicodedata

from app.models import ExtractedText, NormalizedText

logger = logging.getLogger(__name__)


class Normalizer:
    """
    Language-aware text normalizer.
    
    Handles Arabic and English with appropriate rules.
    """

    # Arabic normalization mappings
    ARABIC_ALEF_VARIANTS = re.compile(r'[أإآا]')
    ARABIC_YEH_VARIANTS = re.compile(r'[ىي]')
    ARABIC_DIACRITICS = re.compile(r'[\u064B-\u0652]')

    def normalize(self, extracted: ExtractedText) -> NormalizedText:
        """
        Normalize extracted text.
        """
        # Combine all page text
        raw_text = "\n\n".join(page.text for page in extracted.pages)
        original_length = len(raw_text)

        changes = []
        text = raw_text

        # Step 1: Unicode normalization (NFC)
        text = unicodedata.normalize("NFC", text)
        if text != raw_text:
            changes.append("unicode_nfc")

        # Step 2: Fix encoding issues
        text = self._fix_encoding(text)
        if "encoding" not in changes and text != raw_text:
            changes.append("encoding_fix")

        # Step 3: Normalize whitespace
        text = self._normalize_whitespace(text)
        changes.append("whitespace")

        # Step 4: Language-specific normalization
        if extracted.source_language == "ar":
            text = self._normalize_arabic(text)
            changes.append("arabic_normalization")
        else:
            text = self._normalize_english(text)
            changes.append("english_normalization")

        # Step 5: Remove OCR artifacts
        text = self._remove_ocr_noise(text)
        changes.append("ocr_cleanup")

        logger.info(
            f"Normalized text: {original_length} → {len(text)} chars, "
            f"changes: {', '.join(changes)}"
        )

        return NormalizedText(
            document_id=extracted.document_id,
            tenant_id=extracted.tenant_id,
            text=text,
            language=extracted.source_language,
            original_length=original_length,
            normalized_length=len(text),
            changes_applied=changes,
        )

    def _fix_encoding(self, text: str) -> str:
        """Fix common encoding issues."""
        replacements = {
            '\x00': '',
            '\ufffd': '',
            'â€™': "'",
            'â€"': "—",
            'â€œ': '"',
            'â€': '"',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace characters."""
        # Replace various whitespace with standard space
        text = re.sub(r'[\t\r\f\v]+', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)
        # Normalize newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip lines
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text.strip()

    def _normalize_arabic(self, text: str) -> str:
        """Arabic-specific normalization."""
        # Normalize alef variants
        text = self.ARABIC_ALEF_VARIANTS.sub('ا', text)
        # Normalize yeh
        text = self.ARABIC_YEH_VARIANTS.sub('ي', text)
        # Keep diacritics (tashkeel) for now - configurable
        return text

    def _normalize_english(self, text: str) -> str:
        """English-specific normalization."""
        # Smart quotes to straight
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        # Ligatures
        ligatures = [('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬀ', 'ff'), ('ﬃ', 'ffi')]
        for lig, rep in ligatures:
            text = text.replace(lig, rep)
        return text

    def _remove_ocr_noise(self, text: str) -> str:
        """Remove common OCR artifacts."""
        # Remove isolated single characters that are likely noise
        text = re.sub(r'\s[^\w\s]\s', ' ', text)
        # Remove repeated punctuation
        text = re.sub(r'([.!?]){3,}', r'\1\1\1', text)
        # Remove lines that are just numbers or symbols
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and (len(stripped) > 3 or stripped.isalpha()):
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)


def get_normalizer() -> Normalizer:
    """Get normalizer instance."""
    return Normalizer()
