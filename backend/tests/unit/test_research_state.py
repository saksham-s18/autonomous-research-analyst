from uuid import uuid4

from app.graph.state import ResearchState


def test_research_state_accepts_initial_state() -> None:
    state: ResearchState = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "pending",
        "research_plan": [],
        "current_subquestion": None,
        "completed_subquestions": [],
        "evidence": [],
        "sources": [],
        "conflicts": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    assert state["status"] == "pending"
    assert state["research_plan"] == []
    assert state["research_iterations"] == 0
    assert state["max_research_iterations"] == 3
    assert state["final_report"] is None