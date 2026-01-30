"""
Extraction orchestrator and job worker.
"""

import logging
import time
from datetime import UTC, datetime
from uuid import UUID

from extraction_service.adapters import (
    AudioPreprocessor,
    ImagePreprocessor,
    PDFProcessor,
    get_language_detector,
    get_ocr_service,
    get_stt_service,
)
from extraction_service.domain import (
    ExtractionResult,
    ExtractionType,
    OCRResult,
    STTResult,
)

logger = logging.getLogger(__name__)


class ExtractionWorker:
    """
    Worker for processing extraction jobs.

    Handles routing to OCR or STT based on file category.
    """

    def __init__(self):
        self.ocr_service = get_ocr_service()
        self.stt_service = get_stt_service()
        self.language_detector = get_language_detector()
        self.image_preprocessor = ImagePreprocessor()
        self.audio_preprocessor = AudioPreprocessor()
        self.pdf_processor = PDFProcessor()

    async def process(
        self,
        document_id: str,
        tenant_id: UUID,
        file_category: str,
        content_type: str,
        file_bytes: bytes,
    ) -> ExtractionResult:
        """
        Process a document for text extraction.

        Routes to OCR or STT based on file category.
        """
        time.time()

        if file_category in ("DOCUMENT", "IMAGE"):
            result = await self._process_ocr(
                document_id, file_category, content_type, file_bytes
            )
            extraction_type = ExtractionType.OCR
            result_data = result.to_dict()
            mean_confidence = result.mean_confidence
            detected_language = None

            # Detect language from extracted text
            if result.full_text:
                lang_result = self.language_detector.detect(result.full_text)
                detected_language = lang_result.language

            model_version = result.model_version
            processing_time = result.processing_time_ms

        elif file_category in ("AUDIO", "VIDEO"):
            result = await self._process_stt(
                document_id, content_type, file_bytes
            )
            extraction_type = ExtractionType.STT
            result_data = result.to_dict()
            mean_confidence = result.mean_confidence
            detected_language = result.detected_language
            model_version = result.model_version
            processing_time = result.processing_time_ms

        else:
            raise ValueError(f"Unknown file category: {file_category}")

        return ExtractionResult(
            id=f"ext_{document_id}",
            document_id=document_id,
            tenant_id=tenant_id,
            extraction_type=extraction_type,
            result_data=result_data,
            model_version=model_version,
            processing_time_ms=processing_time,
            mean_confidence=mean_confidence,
            detected_language=detected_language,
            created_at=datetime.now(UTC),
        )

    async def _process_ocr(
        self,
        document_id: str,
        file_category: str,
        content_type: str,
        file_bytes: bytes,
    ) -> OCRResult:
        """Process document/image with OCR."""
        if content_type == "application/pdf":
            # Extract pages from PDF
            pages = self.pdf_processor.extract_pages(file_bytes)
            # Preprocess each page
            preprocessed = [
                self.image_preprocessor.preprocess(p)
                for p in pages
            ]
            return await self.ocr_service.process_document(document_id, preprocessed)
        else:
            # Single image
            preprocessed = self.image_preprocessor.preprocess(file_bytes)
            page_result = await self.ocr_service.process_image(document_id, preprocessed)
            return OCRResult(
                document_id=document_id,
                pages=[page_result],
                total_pages=1,
                processing_time_ms=0,  # Will be set by caller
                model_version=self.ocr_service.adapter.model_version,
            )

    async def _process_stt(
        self,
        document_id: str,
        content_type: str,
        file_bytes: bytes,
    ) -> STTResult:
        """Process audio/video with STT."""
        # Preprocess audio
        audio_path = await self.audio_preprocessor.preprocess(
            file_bytes, content_type, document_id
        )

        try:
            return await self.stt_service.transcribe(document_id, audio_path)
        finally:
            # Cleanup temp files
            self.audio_preprocessor.cleanup(document_id)


def get_extraction_worker() -> ExtractionWorker:
    """Get extraction worker instance."""
    return ExtractionWorker()
