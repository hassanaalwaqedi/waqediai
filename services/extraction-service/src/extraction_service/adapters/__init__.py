"""Adapters package."""

from extraction_service.adapters.kafka_handler import (
    ExtractionKafkaHandler,
    get_kafka_handler,
)
from extraction_service.adapters.language import LanguageDetector, get_language_detector
from extraction_service.adapters.ocr import EasyOCRAdapter, OCRService, get_ocr_service
from extraction_service.adapters.preprocessors import (
    AudioPreprocessor,
    ImagePreprocessor,
    PDFProcessor,
)
from extraction_service.adapters.stt import STTService, WhisperAdapter, get_stt_service

__all__ = [
    "OCRService",
    "EasyOCRAdapter",
    "get_ocr_service",
    "STTService",
    "WhisperAdapter",
    "get_stt_service",
    "ImagePreprocessor",
    "AudioPreprocessor",
    "PDFProcessor",
    "LanguageDetector",
    "get_language_detector",
    "ExtractionKafkaHandler",
    "get_kafka_handler",
]
