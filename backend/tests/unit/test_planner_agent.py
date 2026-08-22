import pytest
from pydantic import BaseModel

from app.agents.planner import PlannerAgent, ResearchPlanOutput
from app.llm.client import LLMClient


class FakeLLMClient(LLMClient):
    def __init__(self) -> None:
        self.last_prompt: str | None = None

    async def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
    ) -> BaseModel:
        self.last_prompt = prompt

        return ResearchPlanOutput(
            goal="Analyze the economic effects of AI automation.",
            subquestions=[
                "What are the employment effects?",
                "What are the productivity effects?",
            ],
        )


@pytest.mark.asyncio
async def test_planner_agent_creates_research_plan() -> None:
    client = FakeLLMClient()
    agent = PlannerAgent(client)

    result = await agent.create_plan(
        "What are the economic effects of AI automation?"
    )

    assert isinstance(result, ResearchPlanOutput)
    assert result.goal == (
        "Analyze the economic effects of AI automation."
    )
    assert len(result.subquestions) == 2
    assert client.last_prompt is not None
    assert "economic effects of AI automation" in client.last_prompt