from uuid import uuid4

from app.graph.state import ResearchState


def test_research_state_supports_sources_and_evidence() -> None:
    state: ResearchState = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "researching",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects?",
            ],
        },
        "current_subquestion": "What are the employment effects?",
        "completed_subquestions": [],
        "evidence": [
            {
                "subquestion": "What are the employment effects?",
                "claim": "AI automation can change demand for routine tasks.",
                "source_url": "https://example.com/report",
                "relevance": 0.9,
            }
        ],
        "sources": [
            {
                "title": "Example Research Report",
                "url": "https://example.com/report",
                "publisher": "Example Organization",
                "published_at": "2026-01-01",
            }
        ],
        "conflicts": [],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    assert len(state["sources"]) == 1
    assert len(state["evidence"]) == 1
    assert state["evidence"][0]["relevance"] == 0.9


def test_research_state_supports_conflicts() -> None:
    state: ResearchState = {
        "research_id": uuid4(),
        "question": "What are the effects of AI automation?",
        "status": "evaluating",
        "research_plan": {
            "goal": "What are the effects of AI automation?",
            "subquestions": [
                "What are the employment effects?",
            ],
        },
        "current_subquestion": "What are the employment effects?",
        "completed_subquestions": [],
        "evidence": [],
        "sources": [],
        "conflicts": [
            {
                "topic": "Employment",
                "claims": [
                    "Automation may increase productivity.",
                    "Automation may displace some workers.",
                ],
                "explanation": "The sources emphasize different effects.",
            }
        ],
        "draft_report": None,
        "final_report": None,
        "confidence": None,
        "error": None,
    }

    assert len(state["conflicts"]) == 1
    assert state["conflicts"][0]["topic"] == "Employment"
    assert len(state["conflicts"][0]["claims"]) == 2