from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "autonomous-research-analyst",
    }


def test_request_logging_middleware() -> None:
    from unittest.mock import patch

    with patch("app.main.logger") as mock_logger:
        response = client.get("/api/health")

    assert response.status_code == 200
    mock_logger.info.assert_any_call(
        "http_request_finished",
        extra={
            "method": "GET",
            "path": "/api/health",
            "status_code": 200,
            "duration_ms": mock_logger.info.call_args_list[-1][1]["extra"]["duration_ms"],
        },
    )
