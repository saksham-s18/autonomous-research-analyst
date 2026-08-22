import pytest

from app.agents.evidence import EvidenceAgent, EvidenceOutput
from app.llm.client import LLMClient


class FakeLLMClient(LLMClient):
    """Fake LLM for evidence tests."""

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[EvidenceOutput],
    ) -> EvidenceOutput:
        return EvidenceOutput(
            claim="AI automation can increase productivity.",
            supporting_text=(
                "The source reports productivity improvements "
                "from AI adoption."
            ),
            relevance=0.95,
            confidence=0.90,
        )


@pytest.mark.asyncio
async def test_evidence_agent_extracts_structured_evidence() -> None:
    agent = EvidenceAgent(FakeLLMClient())

    result = await agent.extract(
        subquestion="How does AI affect productivity?",
        source_url="https://example.com/research",
        content=(
            "AI adoption can improve productivity by "
            "automating repetitive tasks."
        ),
    )

    assert isinstance(result, EvidenceOutput)
    assert result.relevance == 0.95
    assert result.confidence == 0.90
    assert "productivity" in result.claim.lower()