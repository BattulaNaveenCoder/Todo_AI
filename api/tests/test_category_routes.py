from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routes.categories import get_category_service
from app.schemas.category import CategoryResponse


def make_category_response(
    id: int = 1,
    name: str = "Work",
) -> CategoryResponse:
    """Build a CategoryResponse instance with default test values."""
    return CategoryResponse(
        id=id,
        name=name,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 1, 12, 0, 0),
    )


@pytest.fixture
def mock_service() -> MagicMock:
    """Provide a fully-stubbed mock CategoryService."""
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
    app.dependency_overrides[get_category_service] = lambda: mock_service
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# GET /api/v1/categories
# ---------------------------------------------------------------------------


async def test_list_categories_returns_200_with_empty_list(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/categories returns 200 and an empty list when no categories exist."""
    mock_service.get_all.return_value = []

    response = await client.get("/api/v1/categories")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_categories_returns_200_with_categories(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/categories returns 200 and the list of categories."""
    categories = [
        make_category_response(id=1, name="Work"),
        make_category_response(id=2, name="Personal"),
    ]
    mock_service.get_all.return_value = categories

    response = await client.get("/api/v1/categories")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Work"
    assert data[1]["name"] == "Personal"


# ---------------------------------------------------------------------------
# POST /api/v1/categories
# ---------------------------------------------------------------------------


async def test_create_category_returns_201(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """POST /api/v1/categories with valid payload returns 201 with the new category."""
    category = make_category_response(id=1, name="Shopping")
    mock_service.create.return_value = category

    response = await client.post("/api/v1/categories", json={"name": "Shopping"})

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Shopping"


async def test_create_category_with_empty_name_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/categories with an empty name returns 422."""
    response = await client.post("/api/v1/categories", json={"name": ""})

    assert response.status_code == 422


async def test_create_category_with_missing_name_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/categories without a name field returns 422."""
    response = await client.post("/api/v1/categories", json={})

    assert response.status_code == 422


async def test_create_category_with_name_too_long_returns_422(
    client: AsyncClient,
) -> None:
    """POST /api/v1/categories with a 101-character name returns 422."""
    long_name = "A" * 101

    response = await client.post("/api/v1/categories", json={"name": long_name})

    assert response.status_code == 422


async def test_create_category_duplicate_name_returns_409(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """POST /api/v1/categories with a duplicate name returns 409."""
    mock_service.create.side_effect = HTTPException(
        status_code=409,
        detail="Category with name 'Work' already exists",
    )

    response = await client.post("/api/v1/categories", json={"name": "Work"})

    assert response.status_code == 409
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# GET /api/v1/categories/{id}
# ---------------------------------------------------------------------------


async def test_get_category_returns_200_when_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/categories/{id} returns 200 with the category when it exists."""
    category = make_category_response(id=5, name="Found")
    mock_service.get_by_id.return_value = category

    response = await client.get("/api/v1/categories/5")

    assert response.status_code == 200
    assert response.json()["id"] == 5
    assert response.json()["name"] == "Found"


async def test_get_category_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """GET /api/v1/categories/{id} returns 404 when not found."""
    mock_service.get_by_id.side_effect = HTTPException(
        status_code=404, detail="Category with id 99 not found"
    )

    response = await client.get("/api/v1/categories/99")

    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# PUT /api/v1/categories/{id}
# ---------------------------------------------------------------------------


async def test_update_category_returns_200(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/categories/{id} returns 200 with the updated category."""
    updated = make_category_response(id=3, name="Updated Name")
    mock_service.update.return_value = updated

    response = await client.put(
        "/api/v1/categories/3", json={"name": "Updated Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


async def test_update_category_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/categories/{id} returns 404 when the category does not exist."""
    mock_service.update.side_effect = HTTPException(
        status_code=404, detail="Category with id 999 not found"
    )

    response = await client.put("/api/v1/categories/999", json={"name": "X"})

    assert response.status_code == 404
    assert "detail" in response.json()


async def test_update_category_duplicate_name_returns_409(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """PUT /api/v1/categories/{id} returns 409 when the name conflicts."""
    mock_service.update.side_effect = HTTPException(
        status_code=409,
        detail="Category with name 'Taken' already exists",
    )

    response = await client.put("/api/v1/categories/3", json={"name": "Taken"})

    assert response.status_code == 409
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# DELETE /api/v1/categories/{id}
# ---------------------------------------------------------------------------


async def test_delete_category_returns_204(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """DELETE /api/v1/categories/{id} returns 204 on success."""
    mock_service.delete.return_value = None

    response = await client.delete("/api/v1/categories/1")

    assert response.status_code == 204


async def test_delete_category_returns_404_when_not_found(
    client: AsyncClient, mock_service: MagicMock
) -> None:
    """DELETE /api/v1/categories/{id} returns 404 when not found."""
    mock_service.delete.side_effect = HTTPException(
        status_code=404, detail="Category with id 999 not found"
    )

    response = await client.delete("/api/v1/categories/999")

    assert response.status_code == 404
    assert "detail" in response.json()
