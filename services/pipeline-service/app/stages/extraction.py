"""
Document extraction stage.

Extracts text from PDFs, images, and text files.
"""

import io
import logging
import time
from pathlib import Path

from app.models import (
    DocumentInput,
    ExtractedText,
    PageText,
    DocumentType,
)
from app.config import get_settings

logger = logging.getLogger(__name__)


class Extractor:
    """
    Multi-format document text extractor.
    
    Handles native PDFs, scanned PDFs, images, and text files.
    """

    def __init__(self):
        settings = get_settings()
        self.ocr_languages = settings.ocr_languages
        self.confidence_threshold = settings.ocr_confidence_threshold
        self._ocr_reader = None

    def _get_ocr_reader(self):
        """Lazy load EasyOCR reader."""
        if self._ocr_reader is None:
            import easyocr
            self._ocr_reader = easyocr.Reader(self.ocr_languages, gpu=False)
        return self._ocr_reader

    def extract(self, document: DocumentInput) -> ExtractedText:
        """
        Extract text from document based on type.
        """
        start_time = time.time()
        extension = document.extension.lower()

        if extension == ".pdf":
            return self._extract_pdf(document, start_time)
        elif extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return self._extract_image(document, start_time)
        elif extension in [".txt", ".md"]:
            return self._extract_text(document, start_time)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def _extract_pdf(self, document: DocumentInput, start_time: float) -> ExtractedText:
        """Extract text from PDF (native or scanned)."""
        import fitz  # PyMuPDF

        pdf = fitz.open(stream=document.content, filetype="pdf")
        pages = []
        total_text = ""
        is_scanned = True

        for page_num, page in enumerate(pdf):
            text = page.get_text()
            if len(text.strip()) > 50:
                is_scanned = False
                pages.append(PageText(
                    page_number=page_num + 1,
                    text=text,
                    confidence=1.0,
                ))
                total_text += text + "\n"

        # If no text found, use OCR
        if is_scanned:
            pages = self._ocr_pdf_pages(pdf)
            total_text = "\n".join(p.text for p in pages)

        pdf.close()

        language = self._detect_language(total_text)
        avg_confidence = sum(p.confidence for p in pages) / max(len(pages), 1)

        return ExtractedText(
            document_id=document.document_id,
            tenant_id=document.tenant_id,
            pages=pages,
            document_type=DocumentType.PDF_SCANNED if is_scanned else DocumentType.PDF_NATIVE,
            source_language=language,
            extraction_confidence=avg_confidence,
            extraction_time_ms=int((time.time() - start_time) * 1000),
        )

    def _ocr_pdf_pages(self, pdf) -> list[PageText]:
        """OCR each page of a scanned PDF."""
        from pdf2image import convert_from_bytes
        import fitz

        pages = []
        reader = self._get_ocr_reader()

        # Convert PDF to images
        pdf_bytes = pdf.write()
        images = convert_from_bytes(pdf_bytes, dpi=200)

        for page_num, image in enumerate(images):
            # Convert PIL to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="PNG")
            img_bytes = img_buffer.getvalue()

            # OCR
            results = reader.readtext(img_bytes)

            text_parts = []
            confidences = []
            bboxes = []

            for bbox, text, conf in results:
                text_parts.append(text)
                confidences.append(conf)
                bboxes.append({"box": bbox, "text": text, "confidence": conf})

            full_text = " ".join(text_parts)
            avg_conf = sum(confidences) / max(len(confidences), 1)

            pages.append(PageText(
                page_number=page_num + 1,
                text=full_text,
                confidence=avg_conf,
                bounding_boxes=bboxes,
            ))

        return pages

    def _extract_image(self, document: DocumentInput, start_time: float) -> ExtractedText:
        """Extract text from image using OCR."""
        reader = self._get_ocr_reader()
        results = reader.readtext(document.content)

        text_parts = []
        confidences = []
        bboxes = []

        for bbox, text, conf in results:
            text_parts.append(text)
            confidences.append(conf)
            bboxes.append({"box": bbox, "text": text, "confidence": conf})

        full_text = " ".join(text_parts)
        avg_conf = sum(confidences) / max(len(confidences), 1)
        language = self._detect_language(full_text)

        return ExtractedText(
            document_id=document.document_id,
            tenant_id=document.tenant_id,
            pages=[PageText(
                page_number=1,
                text=full_text,
                confidence=avg_conf,
                bounding_boxes=bboxes,
            )],
            document_type=DocumentType.IMAGE,
            source_language=language,
            extraction_confidence=avg_conf,
            extraction_time_ms=int((time.time() - start_time) * 1000),
        )

    def _extract_text(self, document: DocumentInput, start_time: float) -> ExtractedText:
        """Extract from plain text file."""
        text = document.content.decode("utf-8", errors="replace")
        language = self._detect_language(text)

        return ExtractedText(
            document_id=document.document_id,
            tenant_id=document.tenant_id,
            pages=[PageText(page_number=1, text=text, confidence=1.0)],
            document_type=DocumentType.TEXT,
            source_language=language,
            extraction_confidence=1.0,
            extraction_time_ms=int((time.time() - start_time) * 1000),
        )

    def _detect_language(self, text: str) -> str:
        """Detect primary language of text."""
        if not text or len(text.strip()) < 20:
            return "en"

        try:
            from langdetect import detect
            return detect(text[:1000])
        except Exception:
            # Fallback: check for Arabic characters
            arabic_chars = sum(1 for c in text[:500] if '\u0600' <= c <= '\u06FF')
            return "ar" if arabic_chars > 50 else "en"


def get_extractor() -> Extractor:
    """Get extractor instance."""
    return Extractor()
