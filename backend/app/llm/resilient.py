"""Resilient LLM client with fallback support."""

from typing import TypeVar

from pydantic import BaseModel

from app.llm.client import LLMClient

T = TypeVar("T", bound=BaseModel)


class ResilientLLMClient(LLMClient):
    """Use a primary LLM and fall back to a secondary LLM."""

    def __init__(
        self,
        primary: LLMClient,
        fallback: LLMClient,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
    ) -> T:
        """Try the primary provider, then use the fallback."""

        try:
            return await self.primary.generate_structured(
                prompt,
                output_schema,
            )
        except Exception:  # noqa: BLE001
            try:
                return await self.fallback.generate_structured(
                    prompt,
                    output_schema,
                )
            except Exception as fallback_error:
                raise RuntimeError(
                    "Both primary and fallback LLM providers failed."
                ) from fallback_error