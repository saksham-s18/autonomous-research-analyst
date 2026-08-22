"""Factories for configured research tools."""

from app.core.config import settings
from app.tools.search import SearchTool, TavilySearchTool


def create_search_tool() -> SearchTool:
    """Create the configured search tool."""

    if not settings.tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not configured.")

    return TavilySearchTool(
        api_key=settings.tavily_api_key,
    )