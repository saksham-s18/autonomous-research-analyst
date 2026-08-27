"""Autonomous research routing policy."""

from dataclasses import dataclass
from typing import Literal

RouteDecision = Literal[
    "research",
    "synthesis",
]


@dataclass(frozen=True)
class ResearchRoutingDecision:
    """Decision produced by the autonomous research router."""

    route: RouteDecision
    reason: str


def decide_research_route(
    *,
    sufficient: bool,
    completed_subquestions: int,
    total_subquestions: int,
    research_iterations: int,
    max_research_iterations: int,
    follow_up_questions: int,
) -> ResearchRoutingDecision:
    """Decide whether research should continue or synthesis should begin."""

    if sufficient:
        return ResearchRoutingDecision(
            route="synthesis",
            reason="Research evidence meets the sufficiency criteria.",
        )

    if research_iterations >= max_research_iterations:
        if follow_up_questions > 0:
            return ResearchRoutingDecision(
                route="synthesis",
                reason=(
                    "Maximum research iterations reached after "
                    "follow-up research."
                ),
            )

        return ResearchRoutingDecision(
            route="research",
            reason=(
                "Maximum planned research iterations reached; "
                "one adaptive follow-up may be generated."
            ),
        )

    if completed_subquestions < total_subquestions:
        return ResearchRoutingDecision(
            route="research",
            reason="Unanswered research subquestions remain.",
        )

    return ResearchRoutingDecision(
        route="research",
        reason=(
            "Research is insufficient despite completing the "
            "planned subquestions."
        ),
    )