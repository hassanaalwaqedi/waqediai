"""
Text normalization service.

Language-aware text normalization with traceability.
"""

import logging
import unicodedata
import re

from language_service.domain import NormalizationChange, NormalizationRecord
from language_service.config import get_settings

logger = logging.getLogger(__name__)


# Language-specific normalization rules
NORMALIZATION_RULES = {
    "ar": {
        "normalize_alef": True,      # ا أ إ آ → ا
        "normalize_yeh": True,       # ى → ي
        "normalize_teh_marbuta": False,
        "remove_diacritics": False,  # Keep tashkeel by default
    },
    "tr": {
        "preserve_dotted_i": True,   # İ/ı distinction important
        "normalize_g_breve": False,
    },
    "en": {
        "smart_quotes": True,        # "" → ""
        "ligatures": True,           # ﬁ → fi
        "normalize_apostrophe": True,
    },
}


class TextNormalizer:
    """
    Language-aware text normalizer.
    
    Applies normalization rules while preserving meaning
    and tracking all changes for auditability.
    """

    def __init__(self, version: str = "v1.0.0"):
        settings = get_settings()
        self.version = settings.normalization_version

    def normalize(self, text: str, language: str = "en") -> NormalizationRecord:
        """
        Normalize text with full traceability.
        
        Args:
            text: Raw text to normalize.
            language: ISO 639-1 language code.
            
        Returns:
            NormalizationRecord with original, normalized, and changes.
        """
        changes: list[NormalizationChange] = []
        normalized = text

        # Step 1: Unicode NFC normalization
        normalized, step_changes = self._unicode_normalize(normalized)
        changes.extend(step_changes)

        # Step 2: OCR cleanup
        normalized, step_changes = self._ocr_cleanup(normalized)
        changes.extend(step_changes)

        # Step 3: Whitespace normalization
        normalized, step_changes = self._normalize_whitespace(normalized)
        changes.extend(step_changes)

        # Step 4: Language-specific normalization
        rules = NORMALIZATION_RULES.get(language, {})
        if language == "ar":
            normalized, step_changes = self._normalize_arabic(normalized, rules)
            changes.extend(step_changes)
        elif language == "en":
            normalized, step_changes = self._normalize_english(normalized, rules)
            changes.extend(step_changes)

        return NormalizationRecord(
            original_text=text,
            normalized_text=normalized,
            changes=changes,
            version=self.version,
            language=language,
        )

    def _unicode_normalize(self, text: str) -> tuple[str, list[NormalizationChange]]:
        """Apply Unicode NFC normalization."""
        normalized = unicodedata.normalize("NFC", text)
        changes = []
        if normalized != text:
            changes.append(NormalizationChange(
                position=0,
                original="[unicode]",
                replacement="[NFC]",
                rule="unicode_nfc",
            ))
        return normalized, changes

    def _ocr_cleanup(self, text: str) -> tuple[str, list[NormalizationChange]]:
        """Clean common OCR errors."""
        changes = []

        # Common OCR substitutions
        ocr_fixes = [
            (r'\bl\b(?=[0-9])', '1', 'ocr_l_to_1'),  # l → 1 before numbers
            (r'(?<=[a-z])0(?=[a-z])', 'o', 'ocr_0_to_o'),  # 0 → o in words
            (r'rn', 'm', 'ocr_rn_to_m'),  # rn → m (common OCR error)
        ]

        for pattern, replacement, rule in ocr_fixes:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                changes.append(NormalizationChange(
                    position=match.start(),
                    original=match.group(),
                    replacement=replacement,
                    rule=rule,
                ))
            text = re.sub(pattern, replacement, text)

        return text, changes

    def _normalize_whitespace(self, text: str) -> tuple[str, list[NormalizationChange]]:
        """Normalize whitespace characters."""
        changes = []

        # Multiple spaces to single
        if '  ' in text:
            changes.append(NormalizationChange(
                position=0,
                original="[multiple spaces]",
                replacement="[single space]",
                rule="whitespace_collapse",
            ))
            text = re.sub(r' +', ' ', text)

        # Normalize newlines
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove trailing whitespace per line
        text = '\n'.join(line.rstrip() for line in text.split('\n'))

        return text, changes

    def _normalize_arabic(
        self, text: str, rules: dict
    ) -> tuple[str, list[NormalizationChange]]:
        """Arabic-specific normalization."""
        changes = []

        if rules.get("normalize_alef"):
            # Normalize alef variations
            alef_pattern = r'[أإآا]'
            if re.search(alef_pattern, text):
                changes.append(NormalizationChange(
                    position=0,
                    original="[alef variants]",
                    replacement="ا",
                    rule="arabic_alef",
                ))
                text = re.sub(alef_pattern, 'ا', text)

        if rules.get("normalize_yeh"):
            # ى → ي
            if 'ى' in text:
                changes.append(NormalizationChange(
                    position=0,
                    original="ى",
                    replacement="ي",
                    rule="arabic_yeh",
                ))
                text = text.replace('ى', 'ي')

        return text, changes

    def _normalize_english(
        self, text: str, rules: dict
    ) -> tuple[str, list[NormalizationChange]]:
        """English-specific normalization."""
        changes = []

        if rules.get("smart_quotes"):
            # Smart quotes to straight
            if '"' in text or '"' in text:
                changes.append(NormalizationChange(
                    position=0,
                    original="[smart quotes]",
                    replacement='"',
                    rule="english_quotes",
                ))
                text = text.replace('"', '"').replace('"', '"')

        if rules.get("ligatures"):
            ligatures = [('ﬁ', 'fi'), ('ﬂ', 'fl'), ('ﬀ', 'ff')]
            for lig, replacement in ligatures:
                if lig in text:
                    changes.append(NormalizationChange(
                        position=0,
                        original=lig,
                        replacement=replacement,
                        rule="english_ligature",
                    ))
                    text = text.replace(lig, replacement)

        return text, changes


def get_text_normalizer() -> TextNormalizer:
    """Get text normalizer instance."""
    return TextNormalizer()
