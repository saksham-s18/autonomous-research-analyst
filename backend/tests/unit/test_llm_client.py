import pytest
from pydantic import BaseModel

from app.llm.client import LLMClient


class ExampleOutput(BaseModel):
    answer: str


class FakeLLMClient(LLMClient):
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ExampleOutput],
    ) -> ExampleOutput:
        return output_schema(answer=f"Generated from: {prompt}")


@pytest.mark.asyncio
async def test_llm_client_returns_structured_output() -> None:
    client = FakeLLMClient()

    result = await client.generate_structured(
        "Test prompt",
        ExampleOutput,
    )

    assert isinstance(result, ExampleOutput)
    assert result.answer == "Generated from: Test prompt"