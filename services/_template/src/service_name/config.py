"""
Service configuration.

Define service-specific settings by extending BaseSettings.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Service-specific settings.

    Add your service configuration here. All settings can be
    overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="service-template")
    service_version: str = Field(default="0.1.0")
    environment: str = Field(default="development")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)

    # Logging
    log_level: str = Field(default="INFO")

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Health
    health_check_path: str = Field(default="/health")
    ready_check_path: str = Field(default="/ready")

    # Add service-specific settings below
    # database_url: str = Field(default="postgresql://localhost/mydb")
    # redis_url: str = Field(default="redis://localhost:6379")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
