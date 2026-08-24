"""Conflict detection agent."""

from pydantic import BaseModel, Field

from app.graph.state import Evidence
from app.llm.client import LLMClient


class ConflictOutput(BaseModel):
    """Structured representation of a potential evidence conflict."""

    topic: str = Field(
        min_length=1,
        max_length=500,
    )

    evidence_a: str = Field(
        min_length=1,
        max_length=2000,
    )

    evidence_b: str = Field(
        min_length=1,
        max_length=2000,
    )

    conflict_type: str = Field(
        min_length=1,
        max_length=100,
    )

    explanation: str = Field(
        min_length=1,
        max_length=3000,
    )

    severity: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ConflictDetectionOutput(BaseModel):
    """Structured response containing detected conflicts."""

    conflicts: list[ConflictOutput]


class ConflictAgent:
    """Detect meaningful disagreements between research evidence."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def detect(
        self,
        subquestion: str,
        evidence: list[Evidence],
    ) -> list[ConflictOutput]:
        """Detect meaningful conflicts among evidence items."""

        if len(evidence) < 2:
            return []

        prompt = self._build_prompt(
            subquestion,
            evidence,
        )

        result = await self.llm_client.generate_structured(
            prompt,
            ConflictDetectionOutput,
        )

        return result.conflicts

    @staticmethod
    def _build_prompt(
        subquestion: str,
        evidence: list[Evidence],
    ) -> str:
        """Build the conflict detection prompt."""

        return (
            "You are a research evidence conflict analyst.\n\n"
            "Research subquestion:\n"
            f"{subquestion}\n\n"
            "Evidence:\n"
            f"{ConflictAgent._format_evidence(evidence)}\n\n"
            "Identify meaningful disagreements between the "
            "provided evidence.\n\n"
            "Important rules:\n"
            "- Do not treat different wording as a conflict.\n"
            "- Do not declare a conflict merely because two claims "
            "use opposite words.\n"
            "- Consider context such as sector, geography, "
            "population, timeframe, and definitions.\n"
            "- An apparent disagreement may be contextual rather "
            "than a true contradiction.\n"
            "- Only identify conflicts supported by the provided "
            "evidence.\n"
            "- Do not invent information.\n"
            "- If there is no meaningful conflict, return an empty "
            "conflicts list.\n\n"
            "For every conflict provide:\n"
            "- topic\n"
            "- evidence_a\n"
            "- evidence_b\n"
            "- conflict_type\n"
            "- explanation\n"
            "- severity from 0 to 1\n"
            "- confidence from 0 to 1"
        )

    @staticmethod
    def _format_evidence(
        evidence: list[Evidence],
    ) -> str:
        """Format evidence for the conflict detection prompt."""

        sections = []

        for index, item in enumerate(evidence, start=1):
            sections.append(
                
                    f"Evidence {index}:\n"
                    f"Claim: {item['claim']}\n"
                    f"Supporting text: {item['supporting_text']}\n"
                    f"Source: {item['source_url']}\n"
                    f"Relevance: {item['relevance']}\n"
                    f"Confidence: {item['confidence']}\n"
                    f"Evidence score: {item['evidence_score']}"
                
            )

        return "\n\n".join(sections)