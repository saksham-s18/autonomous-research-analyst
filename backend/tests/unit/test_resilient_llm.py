import pytest
from pydantic import BaseModel

from app.llm.client import LLMClient
from app.llm.resilient import ResilientLLMClient


class ExampleOutput(BaseModel):
    answer: str


class FailingLLMClient(LLMClient):
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ExampleOutput],
    ) -> ExampleOutput:
        raise RuntimeError("Primary failed")


class WorkingLLMClient(LLMClient):
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ExampleOutput],
    ) -> ExampleOutput:
        return output_schema(answer="Fallback worked")


@pytest.mark.asyncio
async def test_fallback_llm_is_used_when_primary_fails() -> None:
    client = ResilientLLMClient(
        primary=FailingLLMClient(),
        fallback=WorkingLLMClient(),
    )

    result = await client.generate_structured(
        "test",
        ExampleOutput,
    )

    assert result.answer == "Fallback worked"

class AlsoFailingLLMClient(LLMClient):
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ExampleOutput],
    ) -> ExampleOutput:
        raise RuntimeError("Fallback failed")


@pytest.mark.asyncio
async def test_both_llm_providers_failing_raises_error() -> None:
    client = ResilientLLMClient(
        primary=FailingLLMClient(),
        fallback=AlsoFailingLLMClient(),
    )

    with pytest.raises(
        RuntimeError,
        match="Both primary and fallback LLM providers failed",
    ):
        await client.generate_structured(
            "test",
            ExampleOutput,
        )