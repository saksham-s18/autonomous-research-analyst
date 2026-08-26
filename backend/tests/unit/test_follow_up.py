from app.tools.follow_up import generate_follow_up_question


def test_conflict_generates_targeted_follow_up() -> None:
    result = generate_follow_up_question(
        original_question="What are the effects of AI automation?",
        existing_subquestions=[
            "What are the employment effects?"
        ],
        sufficiency_reasons=[
            "Evidence quality is insufficient."
        ],
        conflict_topics=["AI employment"],
    )

    assert result is not None
    assert result.question == (
        "What additional evidence can clarify the conflicting "
        "claims about AI employment?"
    )
    assert "AI employment" in result.reason


def test_sufficiency_gap_generates_follow_up() -> None:
    result = generate_follow_up_question(
        original_question="What are the effects of AI automation?",
        existing_subquestions=[
            "What are the employment effects?"
        ],
        sufficiency_reasons=[
            "Evidence coverage is incomplete."
        ],
        conflict_topics=[],
    )

    assert result is not None
    assert "What additional evidence is needed" in result.question
    assert "Evidence coverage is incomplete." in result.reason


def test_existing_research_generates_generic_follow_up() -> None:
    result = generate_follow_up_question(
        original_question="What are the effects of AI automation?",
        existing_subquestions=[
            "What are the employment effects?"
        ],
        sufficiency_reasons=[],
        conflict_topics=[],
    )

    assert result is not None
    assert "What additional evidence would strengthen" in result.question


def test_empty_question_returns_none() -> None:
    result = generate_follow_up_question(
        original_question="",
        existing_subquestions=[],
        sufficiency_reasons=[],
        conflict_topics=[],
    )

    assert result is None