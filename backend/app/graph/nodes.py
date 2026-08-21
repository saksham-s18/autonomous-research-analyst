"""Nodes used by the research workflow."""

from app.graph.state import ResearchState


def planner_node(state: ResearchState) -> ResearchState:
    """Create an initial research plan."""

    return {
        **state,
        "status": "planning",
        "research_plan": [
            "Identify the main aspects of the research question.",
            "Collect relevant evidence.",
            "Evaluate the collected evidence.",
            "Synthesize the findings.",
        ],
    }


def research_node(state: ResearchState) -> ResearchState:
    """Placeholder for the future research agent."""

    return {
        **state,
        "status": "researching",
        "research_iterations": state["research_iterations"] + 1,
    }


def synthesis_node(state: ResearchState) -> ResearchState:
    """Placeholder for the future synthesis agent."""

    return {
        **state,
        "status": "synthesizing",
        "draft_report": None,
    }

def route_after_research(state: ResearchState) -> str:
    """Decide whether another research iteration is required."""

    if state["research_iterations"] < state["max_research_iterations"]:
        return "research"

    return "synthesis"