from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from app.services.background import run_research_in_background
from app.api.dependencies import get_research_service
from app.schemas.research import (
    ResearchCreate,
    ResearchResponse,
    ResearchStatusResponse,
)
from app.services.research import ResearchService

router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "",
    response_model=ResearchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_research(
    data: ResearchCreate,
    background_tasks: BackgroundTasks,
    service: ResearchService = Depends(get_research_service),  # noqa: B008
) -> ResearchResponse:
    """Create a research session and start research in the background."""

    research_session = await service.create_research_session(
        data.question,
    )

    background_tasks.add_task(
        run_research_in_background,
        research_session.id,
    )

    return ResearchResponse.model_validate(research_session)

@router.get(
    "",
    response_model=list[ResearchResponse],
)
async def list_research(
    service: ResearchService = Depends(get_research_service), #noqa: B008
) -> list[ResearchResponse]:
    """List research sessions."""

    research_sessions = await service.list_research_sessions()

    return [
        ResearchResponse.model_validate(session)
        for session in research_sessions
    ]

@router.get(
    "/{research_id}/status",
    response_model=ResearchStatusResponse,
)
async def get_research_status(
    research_id: UUID,
    service: ResearchService = Depends(get_research_service),  # noqa: B008
) -> ResearchStatusResponse:
    """Get the current status and progress of a research session."""
    research_status = await service.get_research_status(research_id)

    if research_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found.",
        )

    return ResearchStatusResponse.model_validate(research_status)

@router.get(
    "/{research_id}",
    response_model=ResearchResponse,
)
async def get_research(
    research_id: UUID,
    service: ResearchService = Depends(get_research_service), #noqa: B008
) -> ResearchResponse:
    """Get a research session by ID."""

    research_session = await service.get_research_session(research_id)

    if research_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found.",
        )

    return ResearchResponse.model_validate(research_session)


@router.delete(
    "/{research_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_research(
    research_id: UUID,
    service: ResearchService = Depends(get_research_service), #noqa: B008
) -> None:
    """Delete a research session."""

    deleted = await service.delete_research_session(research_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found.",
        )