"""
Language Service Configuration.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Language service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="language-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8004)
    debug: bool = Field(default=False)

    # Database
    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://waqedi:waqedi_dev@localhost:5432/waqedi")
    )

    # Kafka
    kafka_bootstrap_servers: str = Field(default="localhost:9092")
    kafka_topic_extraction: str = Field(default="extraction")
    kafka_topic_language: str = Field(default="language")
    kafka_consumer_group: str = Field(default="language-service")

    # Language Detection
    detection_min_confidence: float = Field(default=0.5)
    detection_high_confidence: float = Field(default=0.8)
    supported_languages: list[str] = Field(default_factory=lambda: ["en", "ar", "tr"])

    # Translation
    default_translation_strategy: str = Field(default="native")  # native, canonical, hybrid
    canonical_language: str = Field(default="en")
    translation_engine: str = Field(default="google")  # google, azure, deepl

    # Normalization
    normalization_version: str = Field(default="v1.0.0")

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
