"""LLM provider abstraction and implementations."""

import asyncio
from abc import ABC, abstractmethod
from typing import TypeVar

from openai import APIConnectionError, AsyncOpenAI, InternalServerError, RateLimitError
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(ABC):
    """Abstract interface for structured LLM generation."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
    ) -> T:
        """Generate and validate structured output from an LLM."""
        raise NotImplementedError


class OpenAICompatibleLLMClient(LLMClient):
    """LLM client for OpenAI-compatible APIs."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 0,
    ) -> None:
        self.model = model
        self.max_retries = max_retries

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[T],
    ) -> T:
        """Generate structured output using the provider."""

        attempt = 0

        while True:
            try:
                completion = (
                    await self.client.beta.chat.completions.parse(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Return only information that "
                                    "satisfies the requested "
                                    "structured schema."
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],
                        response_format=output_schema,
                    )
                )

                message = completion.choices[0].message

                if message.parsed is None:
                    raise RuntimeError(
                        "LLM returned no structured output."
                    )

                return message.parsed

            except (
                InternalServerError,
                RateLimitError,
                APIConnectionError,
            ):
                if attempt >= self.max_retries:
                    raise

                delay = 2**attempt
                await asyncio.sleep(delay)
                attempt += 1