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

    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_timeout: float = 30.0
    tavily_api_key: str | None = None
    tavily_max_results: int = 5
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    openai_timeout: float = 30.0
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins as a cleaned list."""
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    def require_llm_api_key(self) -> str:
        """Return the configured LLM API key or raise a clear error."""

        if not self.llm_api_key:
            raise ValueError("LLM_API_KEY is not configured.")

        return self.llm_api_key


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""
    return Settings()

settings = get_settings()