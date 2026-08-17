from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


configure_logging()

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the Autonomous Multi-Agent Research Analyst.",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Run application startup tasks."""
    logger.info("application_started")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    logger.info("health_check")
    
    return {
        "status": "healthy",
        "service": "autonomous-research-analyst",
    }