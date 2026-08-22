"""Web source fetching abstractions."""

from abc import ABC, abstractmethod


class SourceFetcher(ABC):
    """Abstract interface for fetching source content."""

    @abstractmethod
    async def fetch(self, url: str) -> str:
        """Fetch readable text from a source URL."""
        raise NotImplementedError