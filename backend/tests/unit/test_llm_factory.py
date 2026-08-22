import pytest

from app.core.config import Settings


def test_llm_api_key_is_required() -> None:
    config = Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
        redis_url="redis://localhost:6379/0",
        llm_api_key=None,
    )

    with pytest.raises(ValueError, match="LLM_API_KEY is not configured"):
        config.require_llm_api_key()