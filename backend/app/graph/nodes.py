"""Nodes used by the research workflow."""

import logging

import httpx

from app.agents.evidence import EvidenceAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearchAgent
from app.graph.state import ResearchState
from app.llm.factory import (
    create_fallback_llm_client,
    create_primary_llm_client,
)
from app.llm.resilient import ResilientLLMClient
from app.tools.evidence_ranking import calculate_evidence_score, rank_evidence
from app.tools.factory import create_search_tool
from app.tools.http_fetcher import HttpSourceFetcher
from app.tools.source_quality import assess_source_quality
from app.tools.url_utils import deduplicate_search_results

logger = logging.getLogger(__name__)

async def planner_node(state: ResearchState) -> ResearchState:
    """Generate a research plan using the planner agent."""

    planner = create_planner_agent()

    plan = await planner.create_plan(state["question"])

    return {
        **state,
        "status": "planning",
        "research_plan": {
            "goal": plan.goal,
            "subquestions": plan.subquestions,
        },
        "current_subquestion": None,
        "completed_subquestions": [],
    }

def create_planner_agent() -> PlannerAgent:
    """Create the configured planner agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return PlannerAgent(llm_client)


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

def create_evidence_agent() -> EvidenceAgent:
    """Create the configured evidence extraction agent."""

    llm_client = ResilientLLMClient(
        primary=create_primary_llm_client(),
        fallback=create_fallback_llm_client(),
    )

    return EvidenceAgent(llm_client)

async def research_node(state: ResearchState) -> ResearchState:
    """Research the current subquestion and extract evidence."""

    current = state["current_subquestion"]

    if current is None:
        return {
            **state,
            "status": "researching",
        }

    researcher = create_research_agent()
    fetcher = HttpSourceFetcher()
    evidence_agent = create_evidence_agent()

    results = await researcher.research(
        current,
        max_results=5,
    )

    results = deduplicate_search_results(results)
    sources = []
    
    for result in results:
        quality = assess_source_quality(result["url"])

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

    for result in results:
        try:
            content = await fetcher.fetch(result["url"])

            extracted = await evidence_agent.extract(
                subquestion=current,
                source_url=result["url"],
                content=content,
            )

            source_quality = assess_source_quality(result["url"])

            evidence_score = calculate_evidence_score(
                relevance=extracted.relevance,
                confidence=extracted.confidence,
                source_quality=source_quality.score,
            )  

            evidence.append(
                {
                    "subquestion": current,
                    "claim": extracted.claim,
                    "supporting_text": extracted.supporting_text,
                    "source_url": result["url"],
                    "relevance": extracted.relevance,
                    "confidence": extracted.confidence,
                    "evidence_score": evidence_score,
                }
            )

        except (httpx.HTTPError, RuntimeError) as exc:
            logger.warning(
                "Failed to extract evidence from %s: %s",
                result["url"],
                exc,
            )
            continue

    completed = [
        *state["completed_subquestions"],
        current,
    ]

    all_evidence = [
        *state["evidence"],
        *evidence,
    ]

    return {
        **state,
        "status": "researching",
        "completed_subquestions": completed,
        "sources": [
            *state["sources"],
            *sources,
        ],
        "evidence": rank_evidence(all_evidence),
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

def create_research_agent() -> ResearchAgent:
    """Create the configured research agent."""

    return ResearchAgent(create_search_tool())