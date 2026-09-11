from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.background import run_research_in_background


@pytest.mark.asyncio
async def test_run_research_in_background() -> None:
    research_id = uuid4()

    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    mock_service = MagicMock()
    mock_service.run_research = AsyncMock()

    with (
        patch(
            "app.services.background.AsyncSessionLocal",
            return_value=mock_session,
        ) as session_factory,
        patch(
            "app.services.background.ResearchSessionRepository",
        ) as repository_class,
        patch(
            "app.services.background.ResearchService",
            return_value=mock_service,
        ),
    ):
        await run_research_in_background(research_id)

    session_factory.assert_called_once_with()
    repository_class.assert_called_once_with(mock_session)
    mock_service.run_research.assert_awaited_once_with(research_id)