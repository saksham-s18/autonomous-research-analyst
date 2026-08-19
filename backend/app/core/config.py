from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="Autonomous Research Analyst API",
        description="Application name.",
    )

    app_version: str = Field(
        default="0.1.0",
        description="Current application version.",
    )

    environment: str = Field(
        default="development",
        description="Application environment.",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode.",
    )

    api_v1_prefix: str = Field(
        default="/api",
        description="Base API prefix.",
    )

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins.",
    )

    log_level: str = Field(
        default="INFO",
        description="Application logging level.",
    )

    database_url: str = Field(
        description="Async PostgreSQL database connection URL.",
    )

    redis_url: str = Field(
        description="Redis connection URL.",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a cleaned list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()