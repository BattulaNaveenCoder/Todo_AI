from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.todo import Todo
from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoUpdate


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


def make_execute_result(scalars_result: object) -> MagicMock:
    """Build a mock that mimics the SQLAlchemy execute() return value."""
    result = MagicMock()
    result.scalars.return_value = scalars_result
    return result


@pytest.fixture
def mock_session() -> MagicMock:
    """Provide a mock AsyncSession with all used methods stubbed."""
    session = MagicMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repository(mock_session: MagicMock) -> TodoRepository:
    """Provide a TodoRepository backed by a mock session."""
    return TodoRepository(mock_session)


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


async def test_get_all_returns_empty_list(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """get_all returns an empty list when the table has no rows."""
    scalars = MagicMock()
    scalars.all.return_value = []
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_all()

    assert result == []
    mock_session.execute.assert_awaited_once()


async def test_get_all_returns_todos(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """get_all returns all rows returned by the query."""
    todos = [make_todo(id=1, title="Alpha"), make_todo(id=2, title="Beta")]
    scalars = MagicMock()
    scalars.all.return_value = todos
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_all()

    assert result == todos
    assert len(result) == 2


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


async def test_get_by_id_returns_todo_when_found(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """get_by_id returns the matching Todo when it exists."""
    todo = make_todo(id=10)
    scalars = MagicMock()
    scalars.first.return_value = todo
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_id(10)

    assert result is todo


async def test_get_by_id_returns_none_when_not_found(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """get_by_id returns None when no row matches the given ID."""
    scalars = MagicMock()
    scalars.first.return_value = None
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_id(999)

    assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


async def test_create_adds_todo_and_flushes(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """create adds the new Todo to the session and flushes to obtain its ID."""
    data = TodoCreate(title="Brand New", description="Some detail")

    result = await repository.create(data)

    mock_session.add.assert_called_once()
    added_todo = mock_session.add.call_args[0][0]
    assert isinstance(added_todo, Todo)
    assert added_todo.title == "Brand New"
    assert added_todo.description == "Some detail"
    mock_session.flush.assert_awaited_once()
    assert result is added_todo


async def test_create_defaults_is_completed_to_false(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """create produces a todo with is_completed defaulting to False."""
    data = TodoCreate(title="Check defaults")

    result = await repository.create(data)

    assert result.is_completed is False


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_applies_partial_fields_and_flushes(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """update sets only supplied fields on the todo and flushes."""
    todo = make_todo(id=3, title="Old", is_completed=False)
    data = TodoUpdate(is_completed=True)

    result = await repository.update(todo, data)

    assert result.is_completed is True
    assert result.title == "Old"
    mock_session.flush.assert_awaited_once()


async def test_update_skips_none_fields(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """update does not overwrite existing values with None."""
    todo = make_todo(id=4, title="Keep Me", description="Keep too")
    data = TodoUpdate(title="Changed")

    result = await repository.update(todo, data)

    assert result.title == "Changed"
    assert result.description == "Keep too"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


async def test_delete_removes_todo_and_flushes(
    repository: TodoRepository, mock_session: MagicMock
) -> None:
    """delete calls session.delete on the todo and flushes."""
    todo = make_todo(id=6)

    await repository.delete(todo)

    mock_session.delete.assert_called_once_with(todo)
    mock_session.flush.assert_awaited_once()
