from fastapi import FastAPI

app = FastAPI(
    title="Autonomous Research Analyst API",
    version="0.1.0",
    description="Backend API for the Autonomous Multi-Agent Research Analyst.",
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "autonomous-research-analyst",
    }