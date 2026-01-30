"""
OCR Model Adapter.

Provides abstraction over OCR engines with EasyOCR as primary implementation.
"""

import logging
import time
from typing import Protocol

from extraction_service.config import get_settings
from extraction_service.domain import (
    BoundingBox,
    OCRPageResult,
    OCRResult,
    TextBlock,
)

logger = logging.getLogger(__name__)


class OCRModelAdapter(Protocol):
    """Abstract interface for OCR models."""

    async def extract(
        self,
        image_bytes: bytes,
        languages: list[str] | None = None,
    ) -> OCRPageResult:
        """Extract text from a single image."""
        ...

    def supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        ...

    @property
    def model_version(self) -> str:
        """Return model version string."""
        ...


class EasyOCRAdapter:
    """
    EasyOCR implementation of OCR adapter.

    Supports 80+ languages with GPU acceleration.
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = False,
    ):
        settings = get_settings()
        self.languages = languages or settings.ocr_languages
        self.gpu = gpu or settings.ocr_gpu
        self._reader = None
        self._version = "easyocr-1.7"

    def _get_reader(self):
        """Lazy load EasyOCR reader."""
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu,
            )
        return self._reader

    async def extract(
        self,
        image_bytes: bytes,
        languages: list[str] | None = None,
    ) -> OCRPageResult:
        """Extract text from image using EasyOCR."""
        import io

        import numpy as np
        from PIL import Image

        start_time = time.time()

        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)

        # Run OCR
        reader = self._get_reader()
        results = reader.readtext(image_array, detail=1)

        # Parse results
        blocks = []
        confidences = []

        for bbox, text, confidence in results:
            # EasyOCR returns [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            x = int(min(x_coords))
            y = int(min(y_coords))
            width = int(max(x_coords) - x)
            height = int(max(y_coords) - y)

            blocks.append(TextBlock(
                text=text,
                confidence=confidence,
                bounding_box=BoundingBox(x=x, y=y, width=width, height=height),
                block_type="line",
            ))
            confidences.append(confidence)

        # Compute full text and mean confidence
        full_text = "\n".join(b.text for b in blocks)
        mean_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(f"OCR completed: {len(blocks)} blocks, {mean_confidence:.2f} confidence, {processing_time}ms")

        return OCRPageResult(
            page_number=1,
            blocks=blocks,
            full_text=full_text,
            mean_confidence=mean_confidence,
            detected_language=None,  # Will be detected separately
        )

    def supported_languages(self) -> list[str]:
        return self.languages

    @property
    def model_version(self) -> str:
        return self._version


class OCRService:
    """
    OCR service orchestrating text extraction from documents.
    """

    def __init__(self, adapter: OCRModelAdapter | None = None):
        self.adapter = adapter or EasyOCRAdapter()

    async def process_image(
        self,
        document_id: str,
        image_bytes: bytes,
        page_number: int = 1,
    ) -> OCRPageResult:
        """Process a single image."""
        result = await self.adapter.extract(image_bytes)
        result.page_number = page_number
        return result

    async def process_document(
        self,
        document_id: str,
        pages: list[bytes],
    ) -> OCRResult:
        """Process a multi-page document."""
        start_time = time.time()
        page_results = []

        for i, page_bytes in enumerate(pages, 1):
            page_result = await self.process_image(document_id, page_bytes, i)
            page_results.append(page_result)

        processing_time = int((time.time() - start_time) * 1000)

        return OCRResult(
            document_id=document_id,
            pages=page_results,
            total_pages=len(pages),
            processing_time_ms=processing_time,
            model_version=self.adapter.model_version,
        )


def get_ocr_service() -> OCRService:
    """Get configured OCR service."""
    return OCRService()
