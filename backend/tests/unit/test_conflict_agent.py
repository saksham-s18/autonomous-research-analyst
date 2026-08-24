import pytest

# pyrefly: ignore [missing-import]
from app.agents.conflict import (
    ConflictAgent,
    ConflictDetectionOutput,
    ConflictOutput,
)


class FakeLLMClient:
    """Deterministic LLM client for conflict tests."""

    def __init__(
        self,
        response: ConflictDetectionOutput,
    ) -> None:
        self.response = response
        self.last_prompt = ""

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[ConflictDetectionOutput],
    ) -> ConflictDetectionOutput:
        self.last_prompt = prompt
        return self.response


def make_evidence(
    claim: str,
    supporting_text: str,
    source_url: str,
    evidence_score: float,
) -> dict:
    """Create deterministic evidence for tests."""

    return {
        "subquestion": "What are the employment effects of AI?",
        "claim": claim,
        "supporting_text": supporting_text,
        "source_url": source_url,
        "relevance": 0.90,
        "confidence": 0.85,
        "evidence_score": evidence_score,
    }


@pytest.mark.asyncio
async def test_conflict_agent_returns_structured_conflicts() -> None:
    response = ConflictDetectionOutput(
        conflicts=[
            ConflictOutput(
                topic="AI employment",
                evidence_a="AI creates new jobs.",
                evidence_b="AI displaces existing jobs.",
                conflict_type="contextual",
                explanation=(
                    "The claims concern different effects of "
                    "automation on employment."
                ),
                severity=0.60,
                confidence=0.90,
            )
        ]
    )

    llm = FakeLLMClient(response)
    agent = ConflictAgent(llm)

    evidence = [
        make_evidence(
            "AI creates new jobs.",
            "New AI-related roles are emerging.",
            "https://example.com/a",
            0.90,
        ),
        make_evidence(
            "AI displaces existing jobs.",
            "Some existing roles are automated.",
            "https://example.com/b",
            0.85,
        ),
    ]

    result = await agent.detect(
        "What are the employment effects of AI?",
        evidence,
    )

    assert len(result) == 1
    assert result[0].topic == "AI employment"
    assert result[0].conflict_type == "contextual"
    assert result[0].severity == 0.60
    assert result[0].confidence == 0.90


@pytest.mark.asyncio
async def test_conflict_agent_skips_llm_for_single_evidence() -> None:
    response = ConflictDetectionOutput(conflicts=[])

    llm = FakeLLMClient(response)
    agent = ConflictAgent(llm)

    evidence = [
        make_evidence(
            "AI creates new jobs.",
            "New AI-related roles are emerging.",
            "https://example.com/a",
            0.90,
        )
    ]

    result = await agent.detect(
        "What are the employment effects of AI?",
        evidence,
    )

    assert result == []
    assert llm.last_prompt == ""


@pytest.mark.asyncio
async def test_conflict_agent_includes_evidence_in_prompt() -> None:
    response = ConflictDetectionOutput(conflicts=[])

    llm = FakeLLMClient(response)
    agent = ConflictAgent(llm)

    evidence = [
        make_evidence(
            "AI creates jobs.",
            "Supporting text A.",
            "https://example.com/a",
            0.90,
        ),
        make_evidence(
            "AI removes jobs.",
            "Supporting text B.",
            "https://example.com/b",
            0.80,
        ),
    ]

    await agent.detect(
        "What are the employment effects of AI?",
        evidence,
    )

    assert "AI creates jobs." in llm.last_prompt
    assert "AI removes jobs." in llm.last_prompt
    assert "Supporting text A." in llm.last_prompt
    assert "Supporting text B." in llm.last_prompt
    assert "Evidence score: 0.9" in llm.last_prompt
    assert "Evidence score: 0.8" in llm.last_prompt