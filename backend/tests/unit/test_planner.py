import pytest
from pydantic import ValidationError

from app.agents.planner import ResearchPlanOutput


def test_research_plan_output_accepts_valid_plan() -> None:
    plan = ResearchPlanOutput(
        goal="Analyze the economic effects of AI automation in India.",
        subquestions=[
            "Which industries are most affected?",
            "What are the employment effects?",
            "What are the productivity effects?",
        ],
    )

    assert plan.goal.startswith("Analyze")
    assert len(plan.subquestions) == 3


def test_research_plan_output_rejects_empty_goal() -> None:
    with pytest.raises(ValidationError):
        ResearchPlanOutput(
            goal="",
            subquestions=[
                "What are the employment effects?",
                "What are the productivity effects?",
            ],
        )


def test_research_plan_output_requires_multiple_subquestions() -> None:
    with pytest.raises(ValidationError):
        ResearchPlanOutput(
            goal="Analyze AI automation.",
            subquestions=[
                "What are the effects?",
            ],
        )


def test_research_plan_output_rejects_too_many_subquestions() -> None:
    with pytest.raises(ValidationError):
        ResearchPlanOutput(
            goal="Analyze AI automation.",
            subquestions=[
                f"Research question {index}"
                for index in range(9)
            ],
        )