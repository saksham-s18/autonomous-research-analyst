from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, get_logger

configure_logging()

settings = get_settings()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the Autonomous Multi-Agent Research Analyst.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Handle expected application errors."""

    logger.warning(
        "application_error",
        extra={
            "error_code": exc.code,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle FastAPI request validation errors."""

    logger.warning(
        "request_validation_error",
        extra={
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request contains invalid data.",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected errors without exposing internal details."""

    logger.exception(
        "unexpected_application_error",
        extra={
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
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