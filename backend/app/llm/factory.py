"""Factories for configured LLM clients."""

from app.core.config import settings
from app.llm.client import LLMClient, OpenAICompatibleLLMClient


def create_primary_llm_client() -> LLMClient:
    """Create the primary Gemini client."""

    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is not configured.")

    return OpenAICompatibleLLMClient(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout,
        max_retries=2,
    )


def create_fallback_llm_client() -> LLMClient:
    """Create the OpenAI fallback client."""

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return OpenAICompatibleLLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout=settings.openai_timeout,
    )