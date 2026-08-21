from uuid import uuid4

from app.graph.workflow import build_research_graph


def test_research_workflow_runs() -> None:
    graph = build_research_graph()

    state = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "pending",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [],
        },
        "current_subquestion": None,
        "completed_subquestions": [],
        "evidence": [],
        "sources": [],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    result = graph.invoke(state)

    assert result["status"] == "synthesizing"
    assert result["research_plan"]["goal"] == "What are the effects of AI automation?"
    assert len(result["research_plan"]["subquestions"]) == 3
    assert len(result["completed_subquestions"]) == 3
    assert len(result["sources"]) == 3
    assert len(result["evidence"]) == 3
    assert all(
        item["source_url"] == "https://example.com/research"
        for item in result["evidence"]
    )
    assert all(
    item["subquestion"] in result["completed_subquestions"]
    for item in result["evidence"]
    )
    assert result["current_subquestion"] is None
    assert result["question"] == "What are the effects of AI automation?"