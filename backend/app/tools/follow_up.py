"""Follow-up research question generation utilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FollowUpQuestion:
    """A targeted follow-up research question."""

    question: str
    reason: str


def generate_follow_up_question(
    *,
    original_question: str,
    existing_subquestions: list[str],
    sufficiency_reasons: list[str],
    conflict_topics: list[str],
) -> FollowUpQuestion | None:
    """Generate a deterministic follow-up research question."""

    if not original_question.strip():
        return None

    if conflict_topics:
        topic = conflict_topics[0]

        return FollowUpQuestion(
            question=(
                f"What additional evidence can clarify the conflicting "
                f"claims about {topic}?"
            ),
            reason=(
                f"Further research is needed to investigate the conflict "
                f"about {topic}."
            ),
        )

    if sufficiency_reasons:
        reason = sufficiency_reasons[0]

        return FollowUpQuestion(
            question=(
                f"What additional evidence is needed to answer "
                f"'{original_question}' more reliably?"
            ),
            reason=(
                f"Follow-up research was generated because: {reason}"
            ),
        )

    if existing_subquestions:
        return FollowUpQuestion(
            question=(
                f"What additional evidence would strengthen the answer "
                f"to '{original_question}'?"
            ),
            reason="Existing research does not yet provide sufficient evidence.",
        )

    return None