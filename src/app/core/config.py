"""
Application configuration.

Loads settings from environment variables with validation.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    PROJECT_NAME: str = "Mini-CRM"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    environment: Literal["development", "staging", "production"] = "development"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @computed_field("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Database
    # database_url: PostgresDsn = Field(
    #     default=env.DATABASE_URL
    # )
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=10, ge=0, le=50)
    db_echo: bool = False

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")
    cache_ttl_seconds: int = Field(default=300, ge=0)  # 5 minutes default

    # JWT Authentication
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        min_length=32,
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)

    # API
    api_v1_prefix: str = "/api/v1"

    @computed_field  # type: ignore[misc]
    @property
    def database_url_sync(self) -> str:
        """Synchronous database URL for Alembic migrations."""
        return str(self.database_url).replace(
            "postgresql+asyncpg://", "postgresql://"
        )

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()