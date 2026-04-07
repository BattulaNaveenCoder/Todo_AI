from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.todo import Todo
from app.routes.todos import get_todo_service


def make_todo(
    id: int = 1,
    title: str = "Test Todo",
    description: str | None = None,
    is_completed: bool = False,
) -> Todo:
    """Build a Todo ORM instance with default test values."""
    todo = Todo()
    todo.id = id
    todo.title = title
    todo.description = description
    todo.is_completed = is_completed
    todo.created_at = datetime(2024, 1, 1, 12, 0, 0)
    todo.updated_at = datetime(2024, 1, 1, 12, 0, 0)
    return todo


@pytest.fixture
def mock_service() -> MagicMock:
    """Provide a fully-stubbed mock TodoService."""
    service = MagicMock()
    service.get_all = AsyncMock(return_value=[])
    service.get_by_id = AsyncMock(return_value=None)
    service.create = AsyncMock(return_value=None)
    service.update = AsyncMock(return_value=None)
    service.delete = AsyncMock(return_value=None)
    return service


@pytest.fixture
async def client(mock_service: MagicMock) -> AsyncClient:
    """Provide an AsyncClient with the service dependency overridden."""
    app.dependency_overrides[get_todo_service] = lambda: mock_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/v1/todos
# ---------------------------------------------------------------------------


async def test_list_todos_returns_200_with_empty_list(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/todos returns 200 and an empty list when no todos exist."""
    mock_service.get_all.return_value = []

    response = await client.get("/api/v1/todos")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_todos_returns_200_with_todos(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/todos returns 200 and the list of todos."""
    todos = [make_todo(id=1, title="First"), make_todo(id=2, title="Second")]
    mock_service.get_all.return_value = todos

    response = await client.get("/api/v1/todos")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "First"
    assert data[1]["title"] == "Second"


# ---------------------------------------------------------------------------
# POST /api/v1/todos
# ---------------------------------------------------------------------------


async def test_create_todo_returns_201(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """POST /api/v1/todos with valid payload returns 201 with the new todo."""
    todo = make_todo(id=1, title="My Task")
    mock_service.create.return_value = todo

    response = await client.post("/api/v1/todos", json={"title": "My Task"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "My Task"
    assert data["isCompleted"] is False


async def test_create_todo_with_empty_title_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/todos with an empty title returns 422."""
    response = await client.post("/api/v1/todos", json={"title": ""})

    assert response.status_code == 422


async def test_create_todo_with_title_too_long_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/todos with a 256-character title returns 422."""
    long_title = "A" * 256

    response = await client.post("/api/v1/todos", json={"title": long_title})

    assert response.status_code == 422


async def test_create_todo_with_missing_title_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/todos without a title field returns 422."""
    response = await client.post("/api/v1/todos", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/todos/{id}
# ---------------------------------------------------------------------------


async def test_get_todo_returns_200_when_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/todos/{id} returns 200 with the todo when it exists."""
    todo = make_todo(id=5, title="Found Todo")
    mock_service.get_by_id.return_value = todo

    response = await client.get("/api/v1/todos/5")

    assert response.status_code == 200
    assert response.json()["id"] == 5
    assert response.json()["title"] == "Found Todo"


async def test_get_todo_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/todos/{id} returns 404 with a detail message when not found."""
    mock_service.get_by_id.side_effect = HTTPException(
        status_code=404, detail="Todo with id 99 not found"
    )

    response = await client.get("/api/v1/todos/99")

    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# PUT /api/v1/todos/{id}
# ---------------------------------------------------------------------------


async def test_update_todo_returns_200(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/todos/{id} returns 200 with the updated todo."""
    updated = make_todo(id=3, title="Updated Title", is_completed=True)
    mock_service.update.return_value = updated

    response = await client.put(
        "/api/v1/todos/3", json={"title": "Updated Title", "isCompleted": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["isCompleted"] is True


async def test_update_todo_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/todos/{id} returns 404 when the todo does not exist."""
    mock_service.update.side_effect = HTTPException(
        status_code=404, detail="Todo with id 999 not found"
    )

    response = await client.put("/api/v1/todos/999", json={"title": "X"})

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_update_todo_with_empty_body_returns_200(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/todos/{id} with an empty body returns 200 (all fields optional)."""
    todo = make_todo(id=2, title="Unchanged")
    mock_service.update.return_value = todo

    response = await client.put("/api/v1/todos/2", json={})

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# DELETE /api/v1/todos/{id}
# ---------------------------------------------------------------------------


async def test_delete_todo_returns_204(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """DELETE /api/v1/todos/{id} returns 204 on success."""
    mock_service.delete.return_value = None

    response = await client.delete("/api/v1/todos/1")

    assert response.status_code == 204


async def test_delete_todo_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """DELETE /api/v1/todos/{id} returns 404 with a detail message when not found."""
    mock_service.delete.side_effect = HTTPException(
        status_code=404, detail="Todo with id 999 not found"
    )

    response = await client.delete("/api/v1/todos/999")

    assert response.status_code == 404
    assert "detail" in response.json()
