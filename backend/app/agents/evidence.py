"""Evidence extraction agent."""

from pydantic import BaseModel, Field

from app.llm.client import LLMClient


class EvidenceOutput(BaseModel):
    """Structured evidence extracted from a source."""

    claim: str = Field(
        min_length=1,
        max_length=2000,
    )

    supporting_text: str = Field(
        min_length=1,
        max_length=5000,
    )

    relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class EvidenceAgent:
    """Extract evidence from source content."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def extract(
        self,
        subquestion: str,
        source_url: str,
        content: str,
    ) -> EvidenceOutput:
        """Extract structured evidence from source content."""

        prompt = (
            "You are an evidence extraction agent.\n\n"
            "Research subquestion:\n"
            f"{subquestion}\n\n"
            "Source URL:\n"
            f"{source_url}\n\n"
            "Source content:\n"
            f"{content}\n\n"
            "Extract one important claim that directly "
            "answers the research subquestion.\n"
            "Use only information supported by the source.\n"
            "Do not invent facts."
        )

        return await self.llm_client.generate_structured(
            prompt,
            EvidenceOutput,
        )