
import pytest

from app.agents.synthesis import SynthesisAgent, SynthesisOutput


class FakeLLMClient:
    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[SynthesisOutput],
    ) -> SynthesisOutput:
        assert "Research question:" in prompt
        assert "Evidence:" in prompt
        assert "Conflicts:" in prompt
        assert "AI automation" in prompt
        assert "executive summary" in prompt.lower()
        assert "key findings" in prompt.lower()
        assert "detailed analysis" in prompt.lower()
        assert "conflicting evidence" in prompt.lower()
        assert "limitations" in prompt.lower()
        assert "conclusion" in prompt.lower()
        assert "confidence score" in prompt.lower()

        return SynthesisOutput(
            title="Effects of AI Automation",
            executive_summary=(
                "AI automation affects employment in multiple ways."
            ),
            key_findings=[
                {
                    "claim": "AI can automate routine tasks.",
                    "evidence_ids": ["E1"],
                },
            ],
            detailed_analysis=(
                "Automation can replace some routine activities while "
                "creating new roles around AI systems."
            ),
            conflicting_evidence=[],
            limitations=[
                "The available evidence is limited.",
            ],
            conclusion=(
                "AI automation has both disruptive and "
                "opportunity-creating effects."
            ),
            confidence=0.88,
        )


@pytest.mark.asyncio
async def test_synthesis_agent_generates_report() -> None:
    agent = SynthesisAgent(FakeLLMClient())

    result = await agent.synthesize(
        question="What are the effects of AI automation?",
        evidence=[
            {
                "evidence_id": "E1",
                "subquestion": "What are the employment effects?",
                "claim": "AI can automate routine tasks.",
                "supporting_text": (
                    "Automation can replace some routine activities."
                ),
                "source_url": "https://example.com/source",
                "relevance": 0.9,
                "confidence": 0.85,
                "evidence_score": 0.87,
            }
        ],
        conflicts=[],
    )

    assert result.title == "Effects of AI Automation"
    assert result.executive_summary == (
        "AI automation affects employment in multiple ways."
    )
    assert len(result.key_findings) == 1
    assert result.key_findings[0].claim == (
        "AI can automate routine tasks."
    )
    assert result.key_findings[0].evidence_ids == ["E1"]
    assert result.detailed_analysis.startswith(
        "Automation can replace some routine activities"
    )
    assert result.conflicting_evidence == []
    assert result.limitations == [
        "The available evidence is limited.",
    ]
    assert result.conclusion.startswith(
        "AI automation has both disruptive"
    )
    assert result.confidence == 0.88


@pytest.mark.asyncio
async def test_synthesis_rejects_unknown_evidence_ids() -> None:
    class InvalidEvidenceLLMClient(FakeLLMClient):
        async def generate_structured(
            self,
            prompt: str,
            output_schema: type[SynthesisOutput],
        ) -> SynthesisOutput:
            return SynthesisOutput(
                title="Effects of AI Automation",
                executive_summary=(
                    "AI automation affects employment in multiple ways."
                ),
                key_findings=[
                    {
                        "claim": "AI can automate routine tasks.",
                        "evidence_ids": ["E999"],
                    },
                ],
                detailed_analysis=(
                    "Automation can replace some routine activities."
                ),
                conflicting_evidence=[],
                limitations=[],
                conclusion="AI has both disruptive and beneficial effects.",
                confidence=0.8,
            )

    agent = SynthesisAgent(InvalidEvidenceLLMClient())

    with pytest.raises(
        ValueError,
        match="unknown evidence IDs",
    ):
        await agent.synthesize(
            question="What are the effects of AI automation?",
            evidence=[
                {
                    "evidence_id": "E1",
                    "subquestion": "What are the employment effects?",
                    "claim": "AI can automate routine tasks.",
                    "supporting_text": (
                        "Automation can replace some routine activities."
                    ),
                    "source_url": "https://example.com/source",
                    "relevance": 0.9,
                    "confidence": 0.85,
                    "evidence_score": 0.87,
                }
            ],
            conflicts=[],
        )