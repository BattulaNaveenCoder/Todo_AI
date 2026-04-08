from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService


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


@pytest.fixture
def mock_repo() -> MagicMock:
    """Provide a mock CategoryRepository with all methods stubbed."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.session = MagicMock()
    repo.session.commit = AsyncMock()
    repo.session.refresh = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repo: MagicMock) -> CategoryService:
    """Provide a CategoryService backed by a mock repository."""
    return CategoryService(mock_repo)


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------


async def test_get_all_returns_empty_list(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """get_all returns an empty list when no categories exist."""
    mock_repo.get_all.return_value = []

    result = await service.get_all()

    assert result == []
    mock_repo.get_all.assert_awaited_once()


async def test_get_all_returns_list_of_categories(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """get_all returns all categories from the repository."""
    categories = [make_category(id=1, name="Work"), make_category(id=2, name="Personal")]
    mock_repo.get_all.return_value = categories

    result = await service.get_all()

    assert len(result) == 2
    assert result[0].name == "Work"
    assert result[1].name == "Personal"


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------


async def test_get_by_id_returns_category_when_found(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """get_by_id returns the category when the repository finds it."""
    category = make_category(id=42, name="Found")
    mock_repo.get_by_id.return_value = category

    result = await service.get_by_id(42)

    assert result.id == 42
    assert result.name == "Found"
    mock_repo.get_by_id.assert_awaited_once_with(42)


async def test_get_by_id_raises_404_when_not_found(
    service: CategoryService, mock_repo: MagicMock
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


async def test_create_returns_category_with_populated_id(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """create persists via repository, commits, refreshes, and returns the category."""
    category = make_category(id=1, name="New Category")
    mock_repo.get_by_name.return_value = None
    mock_repo.create.return_value = category

    data = CategoryCreate(name="New Category")
    result = await service.create(data)

    assert result.id == 1
    assert result.name == "New Category"
    mock_repo.create.assert_awaited_once_with(data)
    mock_repo.session.commit.assert_awaited_once()
    mock_repo.session.refresh.assert_awaited_once_with(category)


async def test_create_raises_409_when_name_already_exists(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """create raises HTTPException 409 when a category with the same name exists."""
    existing = make_category(id=1, name="Duplicate")
    mock_repo.get_by_name.return_value = existing

    with pytest.raises(HTTPException) as exc_info:
        await service.create(CategoryCreate(name="Duplicate"))

    assert exc_info.value.status_code == 409
    assert "Duplicate" in exc_info.value.detail


async def test_create_does_not_call_repo_create_on_duplicate(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """create does not persist when a duplicate name is detected."""
    mock_repo.get_by_name.return_value = make_category(name="Taken")

    with pytest.raises(HTTPException):
        await service.create(CategoryCreate(name="Taken"))

    mock_repo.create.assert_not_awaited()


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


async def test_update_returns_updated_category(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """update applies changes and returns the refreshed category."""
    existing = make_category(id=5, name="Old Name")
    updated = make_category(id=5, name="New Name")
    mock_repo.get_by_id.return_value = existing
    mock_repo.get_by_name.return_value = None
    mock_repo.update.return_value = updated

    result = await service.update(5, CategoryUpdate(name="New Name"))

    assert result.name == "New Name"
    mock_repo.session.commit.assert_awaited_once()
    mock_repo.session.refresh.assert_awaited_once_with(updated)


async def test_update_raises_404_when_not_found(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """update raises HTTPException 404 when the category does not exist."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update(999, CategoryUpdate(name="X"))

    assert exc_info.value.status_code == 404


async def test_update_raises_409_when_name_conflicts(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """update raises HTTPException 409 when the new name is already taken."""
    existing = make_category(id=5, name="Original")
    conflicting = make_category(id=10, name="Taken")
    mock_repo.get_by_id.return_value = existing
    mock_repo.get_by_name.return_value = conflicting

    with pytest.raises(HTTPException) as exc_info:
        await service.update(5, CategoryUpdate(name="Taken"))

    assert exc_info.value.status_code == 409
    assert "Taken" in exc_info.value.detail


async def test_update_skips_name_check_when_name_unchanged(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """update does not check for duplicates when the name is unchanged."""
    existing = make_category(id=5, name="Same")
    mock_repo.get_by_id.return_value = existing
    mock_repo.update.return_value = existing

    await service.update(5, CategoryUpdate(name="Same"))

    mock_repo.get_by_name.assert_not_awaited()


async def test_update_with_empty_payload_returns_unchanged(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """update with no fields changed returns the existing category."""
    existing = make_category(id=5, name="Unchanged")
    mock_repo.get_by_id.return_value = existing
    mock_repo.update.return_value = existing

    result = await service.update(5, CategoryUpdate())

    assert result.name == "Unchanged"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


async def test_delete_calls_repository_delete(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """delete retrieves the category then delegates removal to the repository."""
    category = make_category(id=7, name="To Delete")
    mock_repo.get_by_id.return_value = category

    await service.delete(7)

    mock_repo.delete.assert_awaited_once_with(category)
    mock_repo.session.commit.assert_awaited_once()


async def test_delete_raises_404_when_not_found(
    service: CategoryService, mock_repo: MagicMock
) -> None:
    """delete raises HTTPException 404 when the category does not exist."""
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete(999)

    assert exc_info.value.status_code == 404
