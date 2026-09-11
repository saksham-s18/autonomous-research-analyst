"""Nodes used by the research workflow."""

import logging

import httpx

from app.agents.conflict import ConflictAgent
from app.agents.evidence import EvidenceAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearchAgent
from app.agents.synthesis import SynthesisAgent
from app.graph.state import ResearchState
from app.llm.factory import (
    create_fallback_llm_client,
    create_primary_llm_client,
)
from app.llm.resilient import ResilientLLMClient
from app.tools.citations import (
    build_citations,
    map_findings_to_citations,
)
from app.tools.evidence_ranking import calculate_evidence_score, rank_evidence
from app.tools.factory import create_search_tool
from app.tools.follow_up import generate_follow_up_question
from app.tools.http_fetcher import HttpSourceFetcher
from app.tools.report_formatter import format_report_with_citations
from app.tools.research_router import decide_research_route
from app.tools.research_sufficiency import (
    evaluate_research_sufficiency,
)
from app.tools.source_failures import classify_source_failure
from app.tools.source_quality import assess_source_quality
from app.tools.url_utils import deduplicate_search_results

logger = logging.getLogger(__name__)


async def planner_node(state: ResearchState) -> ResearchState:
    """Generate a research plan using the planner agent."""

    logger.info(
        "planner_node_started",
        extra={"research_id": str(state.get("research_id"))},
    )

    planner = create_planner_agent()

    plan = await planner.create_plan(state["question"])

    logger.info(
        "planner_node_completed",
        extra={
            "research_id": str(state.get("research_id")),
            "subquestions_count": len(plan.subquestions),
        },
    )

    return {
        **state,
        "status": "planning",
        "research_plan": {
            "goal": plan.goal,
            "subquestions": plan.subquestions,
        },
        "current_subquestion": None,
        "completed_subquestions": [],
        "research_iterations": 0,
        "max_research_iterations": 3,
    }



def create_planner_agent() -> PlannerAgent:
    """Create the configured planner agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return PlannerAgent(llm_client)


def follow_up_node(state: ResearchState) -> ResearchState:
    """Generate and store an adaptive follow-up research question."""

    subquestions = state["research_plan"]["subquestions"]

    sufficiency = evaluate_research_sufficiency(
        evidence=state["evidence"],
        source_failures=state["source_failures"],
        expected_subquestions=len(subquestions),
        conflicts=len(state["conflicts"]),
    )

    follow_up = generate_follow_up_question(
        original_question=state["question"],
        existing_subquestions=[
            *subquestions,
            *state["follow_up_subquestions"],
        ],
        sufficiency_reasons=list(sufficiency.reasons),
        conflict_topics=[
            conflict["topic"]
            for conflict in state["conflicts"]
        ],
    )

    if follow_up is None:
        return {
            **state,
            "current_subquestion": None,
        }

    return {
        **state,
        "follow_up_subquestions": [
            *state["follow_up_subquestions"],
            follow_up.question,
        ],
        "current_subquestion": None,
        "status": "researching",
    }


def select_subquestion_node(state: ResearchState) -> ResearchState:
    """Select the next unanswered research subquestion."""

    subquestions = state["research_plan"]["subquestions"]

    remaining_planned = [
        subquestion
        for subquestion in subquestions
        if subquestion not in state["completed_subquestions"]
    ]

    if remaining_planned:
        return {
            **state,
            "current_subquestion": remaining_planned[0],
            "status": "researching",
        }

    remaining_follow_ups = [
        subquestion
        for subquestion in state["follow_up_subquestions"]
        if subquestion not in state["completed_subquestions"]
    ]

    if remaining_follow_ups:
        return {
            **state,
            "current_subquestion": remaining_follow_ups[0],
            "status": "researching",
        }

    return {
        **state,
        "current_subquestion": None,
    }


def create_evidence_agent() -> EvidenceAgent:
    """Create the configured evidence extraction agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return EvidenceAgent(llm_client)


def create_synthesis_agent() -> SynthesisAgent:
    """Create the configured synthesis agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return SynthesisAgent(llm_client)


def create_conflict_agent() -> ConflictAgent:
    """Create the configured conflict detection agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return ConflictAgent(llm_client)


async def research_node(state: ResearchState) -> ResearchState:
    """Research the current subquestion and extract evidence."""

    current = state["current_subquestion"]

    if current is None:
        return {
            **state,
            "status": "researching",
        }

    research_iterations = state["research_iterations"] + 1

    researcher = create_research_agent()
    fetcher = HttpSourceFetcher()
    evidence_agent = create_evidence_agent()

    sources = []

    if state["retry_urls"]:
        logger.info(
            "research_retry_started",
            extra={
                "research_id": str(state.get("research_id")),
                "retry_urls_count": len(state["retry_urls"]),
                "iteration": research_iterations,
            },
        )
        results = [
            {
                "title": "Retry source",
                "url": url,
                "snippet": "",
            }
            for url in state["retry_urls"]
        ]
    else:
        logger.info(
            "research_subquestion_started",
            extra={
                "research_id": str(state.get("research_id")),
                "subquestion": current,
                "iteration": research_iterations,
            },
        )
        results = await researcher.research(
            current,
            max_results=5,
        )
        results = deduplicate_search_results(results)


    for result in results:
        quality = assess_source_quality(result["url"])

        if not state["retry_urls"]:
            sources.append(
                {
                    "title": result["title"],
                    "url": result["url"],
                    "publisher": None,
                    "published_at": None,
                    "quality_score": quality.score,
                    "quality_category": quality.category,
                    "quality_reasons": list(quality.reasons),
                }
            )

    evidence = []
    source_failures = []
    successful_retry_urls = set()

    for result in results:
        try:
            content = await fetcher.fetch(result["url"])

        except httpx.HTTPError as exc:
            error_type, error_message, retryable = (
                classify_source_failure("fetch", exc)
            )

            source_failures.append(
                {
                    "url": result["url"],
                    "stage": "fetch",
                    "error_type": error_type,
                    "error_message": error_message,
                    "retryable": retryable,
                }
            )

            logger.warning(
                "Failed to fetch source %s: %s",
                result["url"],
                error_message,
            )
            continue

        try:
            extracted = await evidence_agent.extract(
                subquestion=current,
                source_url=result["url"],
                content=content,
            )

        except RuntimeError as exc:
            error_type, error_message, retryable = (
                classify_source_failure("extract", exc)
            )

            source_failures.append(
                {
                    "url": result["url"],
                    "stage": "extract",
                    "error_type": error_type,
                    "error_message": error_message,
                    "retryable": retryable,
                }
            )

            logger.warning(
                "Failed to extract evidence from %s: %s",
                result["url"],
                error_message,
            )
            continue

        if result["url"] in state["retry_urls"]:
            successful_retry_urls.add(result["url"])

        source_quality = assess_source_quality(result["url"])

        evidence_score = calculate_evidence_score(
            relevance=extracted.relevance,
            confidence=extracted.confidence,
            source_quality=source_quality.score,
        )

        evidence.append(
            {
                "evidence_id": f"E{len(state['evidence']) + len(evidence) + 1}",
                "subquestion": current,
                "claim": extracted.claim,
                "supporting_text": extracted.supporting_text,
                "source_url": result["url"],
                "relevance": extracted.relevance,
                "confidence": extracted.confidence,
                "evidence_score": evidence_score,
            }
        )

    completed = list(state["completed_subquestions"])

    if current not in completed:
        completed.append(current)

    all_evidence = [
        *state["evidence"],
        *evidence,
    ]

    if state["retry_urls"]:
        all_source_failures = list(state["source_failures"])
    else:
        all_source_failures = [
            *state["source_failures"],
            *source_failures,
        ]

    if research_iterations >= state["max_research_iterations"]:
        remaining_retry_urls = []
    else:
        remaining_retry_urls = [
            url
            for url in state["retry_urls"]
            if url not in successful_retry_urls
        ]

        remaining_retry_urls.extend(
            failure["url"]
            for failure in source_failures
            if failure["retryable"]
            and failure["url"] not in remaining_retry_urls
        )

    return {
        **state,
        "status": "researching",
        "completed_subquestions": completed,
        "research_iterations": research_iterations,
        "sources": [
            *state["sources"],
            *sources,
        ],
        "source_failures": all_source_failures,
        "retry_urls": remaining_retry_urls,
        "evidence": rank_evidence(all_evidence),
    }


def route_after_research(state: ResearchState) -> str:
    """Decide whether research should continue or synthesis should begin."""

    if (
        state["retry_urls"]
        and state["research_iterations"] < state["max_research_iterations"]
    ):
        return "retry"

    subquestions = state["research_plan"]["subquestions"]

    remaining = [
        subquestion
        for subquestion in subquestions
        if subquestion not in state["completed_subquestions"]
    ]

    sufficiency = evaluate_research_sufficiency(
        evidence=state["evidence"],
        source_failures=state["source_failures"],
        expected_subquestions=len(subquestions),
        conflicts=len(state["conflicts"]),
    )

    decision = decide_research_route(
        sufficient=sufficiency.sufficient,
        completed_subquestions=len(
            state["completed_subquestions"]
        ),
        total_subquestions=len(subquestions),
        research_iterations=state["research_iterations"],
        max_research_iterations=state["max_research_iterations"],
        follow_up_questions=len(
            state["follow_up_subquestions"]
        ),
    )

    logger.info(
        "research_routing_decision",
        extra={
            "research_id": str(state.get("research_id")),
            "route": decision.route,
            "reason": decision.reason,
            "research_iterations": state["research_iterations"],
        },
    )


    if decision.route == "synthesis":
        return "synthesis"

    if remaining:
        return "select_subquestion"

    return "follow_up"


async def synthesis_node(state: ResearchState) -> ResearchState:
    """Detect conflicts, synthesize findings, and build citations."""

    if len(state["evidence"]) < 2:
        sufficiency = evaluate_research_sufficiency(
            evidence=state["evidence"],
            source_failures=state["source_failures"],
            expected_subquestions=len(
                state["research_plan"]["subquestions"]
            ),
            conflicts=0,
        )

        citations = build_citations(state["evidence"])

        return {
            **state,
            "status": "synthesizing",
            "current_subquestion": None,
            "draft_report": None,
            "citations": citations,
            "finding_citations": [],
            "conflicts": [],
            "sufficiency_score": sufficiency.score,
            "sufficiency_reasons": list(sufficiency.reasons),
        }

    conflict_agent = create_conflict_agent()

    conflicts = []

    subquestions = state["research_plan"]["subquestions"]

    for subquestion in subquestions:
        subquestion_evidence = [
            item
            for item in state["evidence"]
            if item["subquestion"] == subquestion
        ]

        if len(subquestion_evidence) < 2:
            continue

        detected = await conflict_agent.detect(
            subquestion=subquestion,
            evidence=subquestion_evidence,
        )

        conflicts.extend(
            {
                "topic": conflict.topic,
                "claims": [
                    conflict.evidence_a,
                    conflict.evidence_b,
                ],
                "explanation": conflict.explanation,
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "confidence": conflict.confidence,
            }
            for conflict in detected
        )

    sufficiency = evaluate_research_sufficiency(
        evidence=state["evidence"],
        source_failures=state["source_failures"],
        expected_subquestions=len(
            state["research_plan"]["subquestions"]
        ),
        conflicts=len(conflicts),
    )
    citations = build_citations(state["evidence"])

    synthesis_agent = create_synthesis_agent()

    try:
        result = await synthesis_agent.synthesize(
            question=state["question"],
            evidence=state["evidence"],
            conflicts=conflicts,
        )
    except RuntimeError as exc:
        logger.warning(
            "synthesis_generation_failed",
            extra={
                "research_id": str(state.get("research_id")),
                "error": str(exc),
            },
        )

        return {

            **state,
            "status": "synthesis_failed",
            "current_subquestion": None,
            "draft_report": None,
            "final_report": None,
            "confidence": None,
            "conflicts": conflicts,
            "citations": citations,
            "sufficiency_score": sufficiency.score,
            "sufficiency_reasons": list(sufficiency.reasons),
            "error": str(exc),
        }

    finding_citations = map_findings_to_citations(
        [
            finding.model_dump()
            for finding in result.key_findings
        ],
        state["evidence"],
        citations,
    )

    logger.info(
        "synthesis_node_completed",
        extra={
            "research_id": str(state.get("research_id")),
            "confidence": result.confidence,
        },
    )

    return {
        **state,
        "status": "synthesizing",

        "current_subquestion": None,
        "draft_report": result.executive_summary,
        "final_report": format_report_with_citations(
            result.executive_summary,
            citations,
            finding_citations,
            [
                finding.claim
                for finding in result.key_findings
            ],
        ),
        "conflicts": conflicts,
        "citations": citations,
        "finding_citations": finding_citations,
        "sufficiency_score": sufficiency.score,
        "sufficiency_reasons": list(sufficiency.reasons),
        "confidence": result.confidence,
    }


def create_research_agent() -> ResearchAgent:
    """Create the configured research agent."""

    return ResearchAgent(create_search_tool())
