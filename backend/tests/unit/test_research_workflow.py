from uuid import uuid4

from app.graph.workflow import build_research_graph


def test_research_workflow_runs() -> None:
    graph = build_research_graph()

    state = {
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

    result = graph.invoke(state)

    assert result["status"] == "synthesizing"
    assert len(result["research_plan"]) == 4
    assert result["research_iterations"] == 3
    assert result["question"] == "What are the effects of AI automation?"