"""
Media preprocessing utilities.

Handles image, audio, and PDF preprocessing for extraction.
"""

import io
import logging
from pathlib import Path

from extraction_service.config import get_settings

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """
    Prepare images for OCR.

    Applies deskewing, noise removal, and normalization.
    """

    def preprocess(self, image_bytes: bytes) -> bytes:
        """
        Preprocess image for better OCR results.

        Steps:
        1. Convert to RGB if needed
        2. Resize if too large
        3. Basic enhancement
        """
        from PIL import Image, ImageEnhance

        # Load image
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize if too large (max 4000px on longest side)
        max_size = 4000
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)

        # Save to bytes
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()


class AudioPreprocessor:
    """
    Prepare audio for STT.

    Handles format conversion, normalization, and extraction from video.
    """

    def __init__(self):
        settings = get_settings()
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def preprocess(
        self,
        input_bytes: bytes,
        input_format: str,
        document_id: str,
    ) -> Path:
        """
        Preprocess audio for STT.

        Converts to 16kHz mono WAV.
        """
        from pydub import AudioSegment

        # Determine input format
        format_map = {
            "audio/mpeg": "mp3",
            "audio/wav": "wav",
            "video/mp4": "mp4",
            "audio/mp3": "mp3",
        }
        fmt = format_map.get(input_format, "wav")

        # Load audio
        audio = AudioSegment.from_file(io.BytesIO(input_bytes), format=fmt)

        # Convert to 16kHz mono
        audio = audio.set_frame_rate(16000).set_channels(1)

        # Normalize volume
        audio = audio.normalize()

        # Save as WAV
        output_path = self.temp_dir / f"{document_id}.wav"
        audio.export(str(output_path), format="wav")

        logger.info(f"Audio preprocessed: {len(audio)}ms, saved to {output_path}")
        return output_path

    def cleanup(self, document_id: str) -> None:
        """Remove temporary files for document."""
        wav_path = self.temp_dir / f"{document_id}.wav"
        if wav_path.exists():
            wav_path.unlink()


class PDFProcessor:
    """
    Handle PDF documents.

    Converts PDF pages to images for OCR.
    """

    def __init__(self, dpi: int = 200):
        self.dpi = dpi

    def extract_pages(self, pdf_bytes: bytes) -> list[bytes]:
        """
        Convert PDF pages to images.

        Returns list of PNG images.
        """
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(
            pdf_bytes,
            dpi=self.dpi,
            fmt="png",
        )

        result = []
        for image in images:
            output = io.BytesIO()
            image.save(output, format="PNG")
            result.append(output.getvalue())

        logger.info(f"PDF processed: {len(result)} pages extracted")
        return result

    def is_scanned(self, pdf_bytes: bytes) -> bool:
        """
        Detect if PDF is scanned (image-based) vs native text.

        Simple heuristic: check if extractable text is minimal.
        """
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_text = 0
            for page in doc:
                total_text += len(page.get_text())
            doc.close()
            # If less than 100 chars per page, likely scanned
            return total_text < (100 * len(doc))
        except Exception:
            # Assume scanned if we can't check
            return True
