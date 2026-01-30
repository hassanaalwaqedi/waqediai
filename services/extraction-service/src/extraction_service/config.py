"""
Extraction Service Configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Extraction service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="extraction-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003)
    debug: bool = Field(default=False)

    # Database
    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://waqedi:waqedi_dev@localhost:5432/waqedi")
    )

    # Object Storage
    storage_endpoint: str = Field(default="http://localhost:9000")
    storage_access_key: SecretStr = Field(default=SecretStr("waqedi"))
    storage_secret_key: SecretStr = Field(default=SecretStr("waqedi_dev_secret"))
    storage_bucket: str = Field(default="waqedi-documents")

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_documents: str = Field(default="documents")
    kafka_consumer_group: str = Field(default="extraction-service")

    # OCR Configuration
    ocr_languages: list[str] = Field(default_factory=lambda: ["en", "ar", "tr"])
    ocr_gpu: bool = Field(default=False)
    ocr_confidence_threshold: float = Field(default=0.5)

    # STT Configuration
    whisper_model: str = Field(default="base")  # tiny, base, small, medium, large
    whisper_device: str = Field(default="cpu")  # cpu, cuda

    # Processing
    max_concurrent_jobs: int = Field(default=2)
    job_timeout_seconds: int = Field(default=600)
    max_retries: int = Field(default=3)

    # Temp storage
    temp_dir: str = Field(default="/tmp/extraction")

    # Auth
    jwt_public_key: SecretStr = Field(
        default=SecretStr("dev-public-key-change-in-production")
    )

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
