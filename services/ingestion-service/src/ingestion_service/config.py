"""
Ingestion Service Configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ingestion service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="ingestion-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8002)
    debug: bool = Field(default=True)  # Enable docs and debug mode in development

    # Database
    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://waqedi:waqedi_dev@localhost:5432/waqedi")
    )

    # Object Storage (S3-compatible)
    storage_endpoint: str = Field(default="http://localhost:9000")
    storage_access_key: SecretStr = Field(default=SecretStr("waqedi"))
    storage_secret_key: SecretStr = Field(default=SecretStr("waqedi_dev_secret"))
    storage_bucket: str = Field(default="waqedi-documents")
    storage_region: str = Field(default="us-east-1")
    storage_use_ssl: bool = Field(default=False)

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_documents: str = Field(default="documents")

    # Upload Limits
    max_upload_size_mb: int = Field(default=2048)  # 2 GB
    max_pdf_size_mb: int = Field(default=100)
    max_image_size_mb: int = Field(default=50)
    max_audio_size_mb: int = Field(default=500)
    max_video_size_mb: int = Field(default=2048)

    # Rate Limiting
    upload_rate_limit: int = Field(default=10)
    upload_rate_window_seconds: int = Field(default=60)

    # Auth Service
    auth_service_url: str = Field(default="http://localhost:8001")
    jwt_public_key: SecretStr = Field(
        default=SecretStr("dev-public-key-change-in-production")
    )

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Logging
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
