"""LangGraph research workflow."""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    planner_node,
    research_node,
    route_after_research,
    select_subquestion_node,
    synthesis_node,
)
from app.graph.state import ResearchState


def build_research_graph():
    """Build the research workflow graph."""

    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("select_subquestion", select_subquestion_node)
    graph.add_node("research", research_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "select_subquestion")
    graph.add_edge("select_subquestion", "research")

    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "select_subquestion": "select_subquestion",
            "synthesis": "synthesis",
        },
    )

    graph.add_edge("synthesis", END)

    return graph.compile()