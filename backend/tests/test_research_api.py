from uuid import UUID

import httpx
import pytest
import pytest_asyncio

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_create_research_session(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/research",
        json={
            "question": "What are the economic effects of AI automation in India?"
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert UUID(data["id"])
    assert data["question"] == (
        "What are the economic effects of AI automation in India?"
    )
    assert data["status"] == "pending"
    assert data["confidence"] is None
    assert data["final_report"] is None

    delete_response = await client.delete(
        f"/api/research/{data['id']}"
    )

    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_get_research_session(client: httpx.AsyncClient) -> None:
    create_response = await client.post(
        "/api/research",
        json={"question": "How does AI affect software engineering jobs?"},
    )

    assert create_response.status_code == 201

    research_id = create_response.json()["id"]

    response = await client.get(f"/api/research/{research_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == research_id
    assert data["question"] == (
        "How does AI affect software engineering jobs?"
    )

    delete_response = await client.delete(
        f"/api/research/{research_id}"
    )

    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_list_research_sessions(client: httpx.AsyncClient) -> None:
    first = await client.post(
        "/api/research",
        json={"question": "First research question"},
    )
    second = await client.post(
        "/api/research",
        json={"question": "Second research question"},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    first_id = first.json()["id"]
    second_id = second.json()["id"]

    response = await client.get("/api/research")

    assert response.status_code == 200

    data = response.json()
    ids = {item["id"] for item in data}

    assert first_id in ids
    assert second_id in ids

    await client.delete(f"/api/research/{first_id}")
    await client.delete(f"/api/research/{second_id}")


@pytest.mark.asyncio
async def test_get_missing_research_session(
    client: httpx.AsyncClient,
) -> None:
    missing_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"/api/research/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Research session not found."


@pytest.mark.asyncio
async def test_delete_research_session(
    client: httpx.AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/research",
        json={"question": "Question to delete"},
    )

    assert create_response.status_code == 201

    research_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/research/{research_id}",
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/research/{research_id}",
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_create_research_with_invalid_question(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/api/research",
        json={"question": ""},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"