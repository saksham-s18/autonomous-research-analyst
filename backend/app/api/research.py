from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_research_service
from app.schemas.research import ResearchCreate, ResearchResponse
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
    service: ResearchService = Depends(get_research_service), #noqa: B008
) -> ResearchResponse:
    """Create a new research session."""

    research_session = await service.create_research_session(
        data.question,
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