from app.tools.research_router import decide_research_route


def test_sufficient_research_routes_to_synthesis() -> None:
    result = decide_research_route(
        sufficient=True,
        completed_subquestions=3,
        total_subquestions=3,
        research_iterations=1,
        max_research_iterations=3,
        follow_up_questions=0,
    )

    assert result.route == "synthesis"
    assert result.reason == (
        "Research evidence meets the sufficiency criteria."
    )


def test_remaining_subquestions_route_to_research() -> None:
    result = decide_research_route(
        sufficient=False,
        completed_subquestions=2,
        total_subquestions=3,
        research_iterations=1,
        max_research_iterations=3,
        follow_up_questions=0,
    )

    assert result.route == "research"
    assert result.reason == (
        "Unanswered research subquestions remain."
    )


def test_insufficient_completed_plan_routes_to_more_research() -> None:
    result = decide_research_route(
        sufficient=False,
        completed_subquestions=3,
        total_subquestions=3,
        research_iterations=1,
        max_research_iterations=3,
        follow_up_questions=0,
    )

    assert result.route == "research"
    assert result.reason == (
        "Research is insufficient despite completing the "
        "planned subquestions."
    )


def test_max_iterations_allow_one_adaptive_follow_up() -> None:
    result = decide_research_route(
        sufficient=False,
        completed_subquestions=3,
        total_subquestions=3,
        research_iterations=3,
        max_research_iterations=3,
        follow_up_questions=0,
    )

    assert result.route == "research"
    assert result.reason == (
        "Maximum planned research iterations reached; "
        "one adaptive follow-up may be generated."
    )


def test_sufficiency_takes_priority_over_remaining_questions() -> None:
    result = decide_research_route(
        sufficient=True,
        completed_subquestions=1,
        total_subquestions=3,
        research_iterations=1,
        max_research_iterations=3,
        follow_up_questions=0,
    )

    assert result.route == "synthesis"


def test_max_iterations_allow_adaptive_follow_up_when_plan_incomplete() -> None:
    result = decide_research_route(
        sufficient=False,
        completed_subquestions=1,
        total_subquestions=3,
        research_iterations=5,
        max_research_iterations=5,
        follow_up_questions=0,
    )

    assert result.route == "research"
    assert result.reason == (
        "Maximum planned research iterations reached; "
        "one adaptive follow-up may be generated."
    )



def test_max_iterations_after_follow_up_force_synthesis() -> None:
    result = decide_research_route(
        sufficient=False,
        completed_subquestions=4,
        total_subquestions=3,
        research_iterations=3,
        max_research_iterations=3,
        follow_up_questions=1,
    )

    assert result.route == "synthesis"
    assert result.reason == (
        "Maximum research iterations reached after "
        "follow-up research."
    )