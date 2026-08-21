"""LangGraph research workflow."""

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    planner_node,
    research_node,
    route_after_research,
    synthesis_node,
)
from app.graph.state import ResearchState


def build_research_graph():
    """Build the research workflow graph."""

    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("research", research_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "research")

    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "research": "research",
            "synthesis": "synthesis",
        },
    )

    graph.add_edge("synthesis", END)

    return graph.compile()