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
    category_id: int | None = None,
) -> Todo:
    """Build a Todo ORM instance with default test values."""
    todo = Todo()
    todo.id = id
    todo.title = title
    todo.description = description
    todo.is_completed = is_completed
    todo.category_id = category_id
    todo.category = None
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
def mock_category_repo() -> MagicMock:
    """Provide a mock CategoryRepository with all methods stubbed."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def service(mock_repo: MagicMock, mock_category_repo: MagicMock) -> TodoService:
    """Provide a TodoService backed by mock repositories."""
    return TodoService(mock_repo, mock_category_repo)


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

    assert len(result) == 2
    assert result[0].title == "First"
    assert result[1].title == "Second"


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

    assert result.id == 42
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
    mock_repo.get_by_id.return_value = todo

    data = TodoCreate(title="New Todo")
    result = await service.create(data)

    assert result.id == 1
    assert result.title == "New Todo"
    mock_repo.create.assert_awaited_once_with(data)
    mock_repo.session.commit.assert_awaited_once()


async def test_create_calls_commit_and_refresh(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """create always commits then refreshes after persisting."""
    todo = make_todo()
    mock_repo.create.return_value = todo
    mock_repo.get_by_id.return_value = todo

    await service.create(TodoCreate(title="Any"))

    mock_repo.session.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_returns_updated_todo(
    service: TodoService, mock_repo: MagicMock
) -> None:
    """update applies changes and returns the refreshed todo."""
    existing = make_todo(id=5, title="Old Title")
    updated = make_todo(id=5, title="New Title")
    mock_repo.get_by_id.side_effect = [existing, updated]
    mock_repo.update.return_value = updated

    result = await service.update(5, TodoUpdate(title="New Title"))

    assert result.title == "New Title"
    mock_repo.session.commit.assert_awaited_once()


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


# ---------------------------------------------------------------------------
# create / update with category_id
# ---------------------------------------------------------------------------


async def test_create_with_valid_category_id_succeeds(
    service: TodoService,
    mock_repo: MagicMock,
    mock_category_repo: MagicMock,
) -> None:
    """create with an existing category_id succeeds and returns the todo."""
    from app.models.category import Category

    cat = Category()
    cat.id = 10
    cat.name = "Work"
    mock_category_repo.get_by_id.return_value = cat

    todo = make_todo(id=1, title="Task", category_id=10)
    todo.category = cat
    mock_repo.create.return_value = todo
    mock_repo.get_by_id.return_value = todo

    data = TodoCreate(title="Task", category_id=10)
    result = await service.create(data)

    assert result.id == 1
    assert result.category_id == 10
    assert result.category_name == "Work"
    mock_category_repo.get_by_id.assert_awaited_once_with(10)


async def test_create_with_invalid_category_id_raises_404(
    service: TodoService,
    mock_repo: MagicMock,
    mock_category_repo: MagicMock,
) -> None:
    """create with a non-existent category_id raises HTTPException 404."""
    mock_category_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.create(TodoCreate(title="Task", category_id=999))

    assert exc_info.value.status_code == 404
    assert "999" in exc_info.value.detail
    mock_repo.create.assert_not_awaited()


async def test_create_with_none_category_id_skips_validation(
    service: TodoService,
    mock_repo: MagicMock,
    mock_category_repo: MagicMock,
) -> None:
    """create with category_id=None does not call category_repository.get_by_id."""
    todo = make_todo(id=1, title="No Cat")
    mock_repo.create.return_value = todo
    mock_repo.get_by_id.return_value = todo

    await service.create(TodoCreate(title="No Cat"))

    mock_category_repo.get_by_id.assert_not_awaited()


async def test_update_with_valid_category_id_succeeds(
    service: TodoService,
    mock_repo: MagicMock,
    mock_category_repo: MagicMock,
) -> None:
    """update with an existing category_id succeeds and returns the todo."""
    from app.models.category import Category

    cat = Category()
    cat.id = 5
    cat.name = "Personal"
    mock_category_repo.get_by_id.return_value = cat

    existing = make_todo(id=3, title="Old")
    updated = make_todo(id=3, title="Old", category_id=5)
    updated.category = cat
    mock_repo.get_by_id.side_effect = [existing, updated]
    mock_repo.update.return_value = updated

    result = await service.update(3, TodoUpdate(category_id=5))

    assert result.category_id == 5
    assert result.category_name == "Personal"
