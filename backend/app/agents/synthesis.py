"""Research synthesis agent."""

from pydantic import BaseModel, Field

from app.llm.client import LLMClient


class ResearchFinding(BaseModel):
    """A synthesized claim linked to supporting evidence."""

    claim: str = Field(min_length=1, max_length=2000)
    evidence_ids: list[str] = Field(min_length=1, max_length=10)


class SynthesisOutput(BaseModel):
    """Structured research report generated from evidence."""

    title: str = Field(
        min_length=1,
        max_length=500,
    )

    executive_summary: str = Field(
        min_length=1,
        max_length=5000,
    )

    key_findings: list[ResearchFinding] = Field(
        min_length=1,
        max_length=10,
    )

    detailed_analysis: str = Field(
        min_length=1,
        max_length=10000,
    )

    conflicting_evidence: list[str] = Field(
        max_length=10,
    )

    limitations: list[str] = Field(
        max_length=10,
    )

    conclusion: str = Field(
        min_length=1,
        max_length=5000,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class SynthesisAgent:
    """Synthesize evidence into a coherent research report."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def synthesize(
        self,
        question: str,
        evidence: list[dict],
        conflicts: list[dict],
    ) -> SynthesisOutput:
        """Generate a research report from evidence and conflicts."""

        evidence_text = "\n\n".join(
            (
                f"Claim: {item['claim']}\n"
                f"Supporting text: {item['supporting_text']}\n"
                f"Source: {item['source_url']}\n"
                f"Relevance: {item['relevance']}\n"
                f"Confidence: {item['confidence']}\n"
            )
            for item in evidence
        )

        conflicts_text = "\n\n".join(
            (
                f"Topic: {item['topic']}\n"
                f"Claims: {item['claims']}\n"
                f"Explanation: {item['explanation']}\n"
            )
            for item in conflicts
        )

        prompt = (
            "You are a research synthesis agent.\n\n"
            "Research question:\n"
            f"{question}\n\n"
            "Evidence:\n"
            f"{evidence_text or 'No evidence available.'}\n\n"
            "Conflicts:\n"
            f"{conflicts_text or 'No conflicts detected.'}\n\n"
            "Generate a structured research report that directly "
            "answers the research question.\n\n"
            "Report requirements:\n"
            "- Create a clear, specific title.\n"
            "- Write an executive summary of the overall answer.\n"
            "- List the most important evidence-backed key findings.\n"
            "- Each key finding must contain a claim and one or more "
            "supporting evidence IDs.\n"
            "- Use only evidence IDs that appear in the provided evidence.\n"
            "- Do not invent, modify, or guess evidence IDs.\n"
            "- Provide a detailed analysis connecting the evidence "
            "to the research question.\n"
            "- Clearly describe conflicting evidence when present. "
            "If there are no meaningful conflicts, return an empty list.\n"
            "- List important limitations of the available evidence.\n"
            "- Provide a concise conclusion that answers the research "
            "question.\n"
            "- Assign a confidence score between 0 and 1 based on the "
            "quality, relevance, and consistency of the evidence.\n\n"
            "Use only information supported by the provided evidence.\n"
            "Do not invent facts, sources, citations, or evidence IDs.\n"
            "Clearly distinguish conflicting evidence instead of "
            "silently choosing one claim.\n"
            "Return content suitable for a professional research report."
        )

        result = await self.llm_client.generate_structured(
            prompt,
            SynthesisOutput,
        )

        valid_evidence_ids = {
            item["evidence_id"]
            for item in evidence
            if "evidence_id" in item
        }

        for finding in result.key_findings:
            invalid_ids = set(finding.evidence_ids) - valid_evidence_ids

            if invalid_ids:
                raise ValueError(
                    "Synthesis referenced unknown evidence IDs: "
                    f"{sorted(invalid_ids)}"
                )

        return result