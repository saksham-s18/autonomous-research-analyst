"""Nodes used by the research workflow."""

from app.graph.state import ResearchState


def planner_node(state: ResearchState) -> ResearchState:
    """Create an initial research plan from the question."""

    subquestions = [
        f"What are the main aspects of: {state['question']}?",
        f"What evidence exists regarding: {state['question']}?",
        f"What are the potential benefits and risks of: {state['question']}?",
    ]

    research_plan = {
        "goal": state["question"],
        "subquestions": subquestions,
    }

    return {
        **state,
        "status": "planning",
        "research_plan": research_plan,
        "current_subquestion": None,
        "completed_subquestions": [],
    }


def select_subquestion_node(state: ResearchState) -> ResearchState:
    """Select the next unanswered research subquestion."""

    subquestions = state["research_plan"]["subquestions"]

    remaining = [
        subquestion
        for subquestion in subquestions
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

    source = {
        "title": "Placeholder Research Source",
        "url": "https://example.com/research",
        "publisher": "Placeholder Publisher",
        "published_at": None,
    }

    evidence = {
        "subquestion": current,
        "claim": f"Placeholder evidence for: {current}",
        "source_url": source["url"],
        "relevance": 1.0,
    }

    completed = [
        *state["completed_subquestions"],
        current,
    ]

    return {
        **state,
        "status": "researching",
        "completed_subquestions": completed,
        "sources": [*state["sources"], source],
        "evidence": [*state["evidence"], evidence],
    }

def route_after_research(state: ResearchState) -> str:
    """Decide whether another subquestion needs research."""

    subquestions = state["research_plan"]["subquestions"]

    remaining = [
        subquestion
        for subquestion in subquestions
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