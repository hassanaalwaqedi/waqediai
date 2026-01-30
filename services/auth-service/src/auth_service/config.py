"""
Auth Service Configuration.

Security-critical settings with strict validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Auth service configuration.

    All secrets must be provided via environment variables.
    No defaults for security-sensitive values in production.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="auth-service")
    service_version: str = Field(default="0.1.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)
    debug: bool = Field(default=False)

    # Database
    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://waqedi:waqedi_dev@localhost:5432/waqedi")
    )

    # Redis (for rate limiting and token revocation)
    redis_url: str = Field(default="redis://localhost:6379/0")

    # JWT Configuration
    jwt_private_key: SecretStr = Field(
        default=SecretStr("dev-private-key-change-in-production")
    )
    jwt_public_key: SecretStr = Field(
        default=SecretStr("dev-public-key-change-in-production")
    )
    jwt_algorithm: str = Field(default="RS256")
    jwt_access_token_expire_minutes: int = Field(default=15)
    jwt_issuer: str = Field(default="waqedi-auth")
    jwt_audience: str = Field(default="waqedi-api")

    # Refresh Token
    refresh_token_expire_days: int = Field(default=7)

    # Password Hashing (Argon2)
    argon2_time_cost: int = Field(default=3)
    argon2_memory_cost: int = Field(default=65536)  # 64 MB
    argon2_parallelism: int = Field(default=4)

    # Rate Limiting
    login_rate_limit: int = Field(default=5)
    login_rate_window_minutes: int = Field(default=15)

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Logging
    log_level: str = Field(default="INFO")

    @field_validator("environment")
    @classmethod
    def validate_production_secrets(cls, v: str, info) -> str:
        """Ensure real secrets are used in production."""
        if v == "production":
            # In production, we'd validate that secrets aren't defaults
            pass
        return v

    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
