"""HTTP source fetcher."""

import httpx

from app.tools.fetch import SourceFetcher


class HttpSourceFetcher(SourceFetcher):
    """Fetch source pages over HTTP."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    async def fetch(self, url: str) -> str:
        """Fetch page content."""

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "AutonomousResearchAnalyst/1.0",
                },
            )

            response.raise_for_status()

            return response.text