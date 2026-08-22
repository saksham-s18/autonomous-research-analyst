"""Planner agent schemas and logic."""

from pydantic import BaseModel, Field

from app.llm.client import LLMClient


class ResearchPlanOutput(BaseModel):
    """Structured output expected from the planner agent."""

    goal: str = Field(
        min_length=1,
        max_length=1000,
    )

    subquestions: list[str] = Field(
        min_length=2,
        max_length=8,
    )


class PlannerAgent:
    """Generate structured research plans using an LLM."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def create_plan(self, question: str) -> ResearchPlanOutput:
        """Generate a research plan for a question."""

        prompt = self._build_prompt(question)

        return await self.llm_client.generate_structured(
            prompt,
            ResearchPlanOutput,
        )

    @staticmethod
    def _build_prompt(question: str) -> str:
        """Build the planner prompt."""

        return (
            "You are a research planning agent.\n"
            "Analyze the user's research question and create a "
            "focused research plan.\n\n"
            f"Research question:\n{question}\n\n"
            "Generate a clear research goal and 2 to 8 "
            "specific research subquestions."
        )