"""
Speech-to-Text Model Adapter.

Provides abstraction over STT engines with Whisper as primary implementation.
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Protocol

from extraction_service.domain import (
    TranscriptSegment,
    STTResult,
)
from extraction_service.config import get_settings

logger = logging.getLogger(__name__)


class STTModelAdapter(Protocol):
    """Abstract interface for STT models."""

    async def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
    ) -> STTResult:
        """Transcribe audio file."""
        ...

    def supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        ...

    @property
    def model_version(self) -> str:
        """Return model version string."""
        ...


class WhisperAdapter:
    """
    OpenAI Whisper implementation of STT adapter.
    
    Supports multilingual transcription with word-level timestamps.
    """

    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
    ):
        settings = get_settings()
        self.model_name = model_name or settings.whisper_model
        self.device = device or settings.whisper_device
        self._model = None
        self._version = f"whisper-{self.model_name}"

    def _get_model(self):
        """Lazy load Whisper model."""
        if self._model is None:
            import whisper
            self._model = whisper.load_model(self.model_name, device=self.device)
        return self._model

    async def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
    ) -> STTResult:
        """Transcribe audio using Whisper."""
        start_time = time.time()

        model = self._get_model()

        # Transcribe with word timestamps
        result = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,
            verbose=False,
        )

        # Parse segments
        segments = []
        for segment in result.get("segments", []):
            segments.append(TranscriptSegment(
                text=segment["text"].strip(),
                start_time=segment["start"],
                end_time=segment["end"],
                confidence=None,  # Whisper doesn't provide per-segment confidence
                speaker_id=None,
            ))

        # Get duration from last segment
        duration = segments[-1].end_time if segments else 0.0
        detected_language = result.get("language", language or "unknown")

        processing_time = int((time.time() - start_time) * 1000)
        logger.info(
            f"STT completed: {len(segments)} segments, "
            f"{duration:.1f}s audio, {processing_time}ms processing"
        )

        return STTResult(
            document_id="",  # Set by caller
            segments=segments,
            duration_seconds=duration,
            detected_language=detected_language,
            processing_time_ms=processing_time,
            model_version=self._version,
        )

    def supported_languages(self) -> list[str]:
        # Whisper supports 99 languages
        return ["en", "ar", "tr", "de", "fr", "es", "zh", "ja", "ko", "ru"]

    @property
    def model_version(self) -> str:
        return self._version


class STTService:
    """
    STT service orchestrating audio transcription.
    """

    def __init__(self, adapter: STTModelAdapter | None = None):
        settings = get_settings()
        self.adapter = adapter or WhisperAdapter(
            model_name=settings.whisper_model,
            device=settings.whisper_device,
        )

    async def transcribe(
        self,
        document_id: str,
        audio_path: Path,
        language: str | None = None,
    ) -> STTResult:
        """Transcribe an audio file."""
        result = await self.adapter.transcribe(audio_path, language)
        result.document_id = document_id
        return result

    async def transcribe_bytes(
        self,
        document_id: str,
        audio_bytes: bytes,
        suffix: str = ".wav",
        language: str | None = None,
    ) -> STTResult:
        """Transcribe audio from bytes."""
        settings = get_settings()
        temp_dir = Path(settings.temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Write to temp file
        temp_path = temp_dir / f"{document_id}{suffix}"
        try:
            temp_path.write_bytes(audio_bytes)
            return await self.transcribe(document_id, temp_path, language)
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()


def get_stt_service() -> STTService:
    """Get configured STT service."""
    return STTService()
