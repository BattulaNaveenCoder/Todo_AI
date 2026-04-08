from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


def make_category(
    id: int = 1,
    name: str = "Work",
) -> Category:
    """Build a Category ORM instance with default test values."""
    category = Category()
    category.id = id
    category.name = name
    category.created_at = datetime(2024, 1, 1, 12, 0, 0)
    category.updated_at = datetime(2024, 1, 1, 12, 0, 0)
    return category


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
def repository(mock_session: MagicMock) -> CategoryRepository:
    """Provide a CategoryRepository backed by a mock session."""
    return CategoryRepository(mock_session)


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


async def test_get_all_returns_empty_list(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_all returns an empty list when the table has no rows."""
    scalars = MagicMock()
    scalars.all.return_value = []
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_all()

    assert result == []
    mock_session.execute.assert_awaited_once()


async def test_get_all_returns_categories(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_all returns all rows returned by the query."""
    categories = [make_category(id=1, name="Work"), make_category(id=2, name="Personal")]
    scalars = MagicMock()
    scalars.all.return_value = categories
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_all()

    assert result == categories
    assert len(result) == 2


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


async def test_get_by_id_returns_category_when_found(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_by_id returns the matching Category when it exists."""
    category = make_category(id=10, name="Urgent")
    scalars = MagicMock()
    scalars.first.return_value = category
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_id(10)

    assert result is category


async def test_get_by_id_returns_none_when_not_found(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_by_id returns None when no row matches the given ID."""
    scalars = MagicMock()
    scalars.first.return_value = None
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_id(999)

    assert result is None


# ---------------------------------------------------------------------------
# get_by_name
# ---------------------------------------------------------------------------


async def test_get_by_name_returns_category_when_found(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_by_name returns the matching Category when it exists."""
    category = make_category(id=3, name="Home")
    scalars = MagicMock()
    scalars.first.return_value = category
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_name("Home")

    assert result is category


async def test_get_by_name_returns_none_when_not_found(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """get_by_name returns None when no row matches the given name."""
    scalars = MagicMock()
    scalars.first.return_value = None
    mock_session.execute.return_value = make_execute_result(scalars)

    result = await repository.get_by_name("Nonexistent")

    assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


async def test_create_adds_category_and_flushes(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """create adds the new Category to the session and flushes to obtain its ID."""
    data = CategoryCreate(name="Shopping")

    result = await repository.create(data)

    mock_session.add.assert_called_once()
    added_category = mock_session.add.call_args[0][0]
    assert isinstance(added_category, Category)
    assert added_category.name == "Shopping"
    mock_session.flush.assert_awaited_once()
    assert result is added_category


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_applies_name_and_flushes(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """update sets the name field on the category and flushes."""
    category = make_category(id=2, name="Old Name")
    data = CategoryUpdate(name="New Name")

    result = await repository.update(category, data)

    assert result.name == "New Name"
    mock_session.flush.assert_awaited_once()


async def test_update_skips_none_fields(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """update does not overwrite existing values with None."""
    category = make_category(id=4, name="Keep Me")
    data = CategoryUpdate()

    result = await repository.update(category, data)

    assert result.name == "Keep Me"
    mock_session.flush.assert_awaited_once()


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


async def test_delete_removes_category_and_flushes(
    repository: CategoryRepository, mock_session: MagicMock
) -> None:
    """delete calls session.delete on the category and flushes."""
    category = make_category(id=6, name="To Remove")

    await repository.delete(category)

    mock_session.delete.assert_called_once_with(category)
    mock_session.flush.assert_awaited_once()
