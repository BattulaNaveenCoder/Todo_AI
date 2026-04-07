from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate
from app.services.todo import TodoService


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
def mock_repo() -> MagicMock:
    """Provide a mock TodoRepository with all methods stubbed."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.session = MagicMock()
    repo.session.commit = AsyncMock()
    repo.session.refresh = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo: MagicMock) -> TodoService:
    """Provide a TodoService backed by a mock repository."""
    return TodoService(mock_repo)


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


async def test_get_all_returns_empty_list(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """get_all returns an empty list when no todos exist."""
    mock_repo.get_all.return_value = []

    result = await service.get_all()

    assert result == []
    mock_repo.get_all.assert_awaited_once()


async def test_get_all_returns_list_of_todos(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """get_all returns all todos from the repository."""
    todos = [make_todo(id=1, title="First"), make_todo(id=2, title="Second")]
    mock_repo.get_all.return_value = todos

    result = await service.get_all()

    assert result == todos
    assert len(result) == 2


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


async def test_get_by_id_returns_todo_when_found(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """get_by_id returns the todo when the repository finds it."""
    todo = make_todo(id=42)
    mock_repo.get_by_id.return_value = todo

    result = await service.get_by_id(42)

    assert result is todo
    mock_repo.get_by_id.assert_awaited_once_with(42)


async def test_get_by_id_raises_404_when_not_found(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """get_by_id raises HTTPException 404 when the repository returns None."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(99)

    assert exc_info.value.status_code == 404
    assert "99" in exc_info.value.detail


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


async def test_create_returns_todo_with_populated_id(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """create persists via repository, commits, refreshes, and returns the todo."""
    todo = make_todo(id=1, title="New Todo")
    mock_repo.create.return_value = todo

    data = TodoCreate(title="New Todo")
    result = await service.create(data)

    assert result is todo
    mock_repo.create.assert_awaited_once_with(data)
    mock_repo.session.commit.assert_awaited_once()
    mock_repo.session.refresh.assert_awaited_once_with(todo)


async def test_create_calls_commit_and_refresh(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """create always commits then refreshes after persisting."""
    todo = make_todo()
    mock_repo.create.return_value = todo

    await service.create(TodoCreate(title="Any"))

    mock_repo.session.commit.assert_awaited_once()
    mock_repo.session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_returns_updated_todo(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """update applies changes and returns the refreshed todo."""
    existing = make_todo(id=5, title="Old Title")
    updated = make_todo(id=5, title="New Title")
    mock_repo.get_by_id.return_value = existing
    mock_repo.update.return_value = updated

    result = await service.update(5, TodoUpdate(title="New Title"))

    assert result is updated
    mock_repo.session.commit.assert_awaited_once()
    mock_repo.session.refresh.assert_awaited_once_with(updated)


async def test_update_raises_404_when_not_found(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """update raises HTTPException 404 when the todo does not exist."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update(999, TodoUpdate(title="X"))

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


async def test_delete_calls_repository_delete(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """delete retrieves the todo then delegates removal to the repository."""
    todo = make_todo(id=7)
    mock_repo.get_by_id.return_value = todo

    await service.delete(7)

    mock_repo.delete.assert_awaited_once_with(todo)
    mock_repo.session.commit.assert_awaited_once()


async def test_delete_raises_404_when_not_found(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """delete raises HTTPException 404 when the todo does not exist."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete(999)

    assert exc_info.value.status_code == 404
