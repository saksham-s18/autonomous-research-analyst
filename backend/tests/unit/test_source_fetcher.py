import pytest

from app.tools.fetch import SourceFetcher


class FakeSourceFetcher(SourceFetcher):
    """Fake source fetcher for tests."""

    async def fetch(self, url: str) -> str:
        return f"Content from {url}"


@pytest.mark.asyncio
async def test_source_fetcher_returns_content() -> None:
    fetcher = FakeSourceFetcher()

    result = await fetcher.fetch(
        "https://example.com/research"
    )

    assert result == (
        "Content from https://example.com/research"
    )