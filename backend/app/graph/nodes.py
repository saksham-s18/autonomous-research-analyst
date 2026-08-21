"""Nodes used by the research workflow."""

from app.graph.state import ResearchState


def planner_node(state: ResearchState) -> ResearchState:
    """Create an initial research plan from the question."""

    return {
        **state,
        "status": "planning",
        "research_plan": [
            f"What are the main aspects of: {state['question']}?",
            f"What evidence exists regarding: {state['question']}?",
            f"What are the potential benefits and risks of: {state['question']}?",
        ],
        "current_subquestion": None,
        "completed_subquestions": [],
    }


def select_subquestion_node(state: ResearchState) -> ResearchState:
    """Select the next unanswered research subquestion."""

    remaining = [
        subquestion
        for subquestion in state["research_plan"]
        if subquestion not in state["completed_subquestions"]
    ]

    if not remaining:
        return {
            **state,
            "current_subquestion": None,
        }

    return {
        **state,
        "current_subquestion": remaining[0],
        "status": "researching",
    }


def research_node(state: ResearchState) -> ResearchState:
    """Placeholder for the future research agent."""

    current = state["current_subquestion"]

    if current is None:
        return {
            **state,
            "status": "researching",
        }

    completed = [
        *state["completed_subquestions"],
        current,
    ]

    return {
        **state,
        "status": "researching",
        "research_iterations": state["research_iterations"] + 1,
        "completed_subquestions": completed,
    }


def route_after_research(state: ResearchState) -> str:
    """Decide whether another subquestion needs research."""

    remaining = [
        subquestion
        for subquestion in state["research_plan"]
        if subquestion not in state["completed_subquestions"]
    ]

    if remaining:
        return "select_subquestion"

    return "synthesis"


def synthesis_node(state: ResearchState) -> ResearchState:
    """Placeholder for the future synthesis agent."""

    return {
        **state,
        "status": "synthesizing",
        "current_subquestion": None,
        "draft_report": None,
    }