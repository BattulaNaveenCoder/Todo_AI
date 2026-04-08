import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


def get_category_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryRepository:
    """Provide a CategoryRepository for the current request.

    Args:
        session: Injected async database session.

    Returns:
        CategoryRepository bound to the session.
    """
    return CategoryRepository(session)


def get_category_service(
    repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> CategoryService:
    """Provide a CategoryService for the current request.

    Args:
        repository: Injected CategoryRepository.

    Returns:
        CategoryService bound to the repository.
    """
    return CategoryService(repository)


@router.get(
    "",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories",
    description="Returns all categories ordered by name ascending.",
)
async def list_categories(
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[CategoryResponse]:
    """List all categories.

    Args:
        service: Injected CategoryService.

    Returns:
        List of CategoryResponse objects.
    """
    return await service.get_all()  # type: ignore[return-value] — service returns list[Category], FastAPI serialises to CategoryResponse


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Creates a new category with the provided name. Name must be unique.",
)
async def create_category(
    payload: CategoryCreate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    """Create a new category.

    Args:
        payload: Validated create payload.
        service: Injected CategoryService.

    Returns:
        The created CategoryResponse.
    """
    return await service.create(payload)  # type: ignore[return-value] — service returns Category ORM, FastAPI serialises to CategoryResponse


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a category by ID",
    description="Returns a single category by its ID.",
)
async def get_category(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    """Retrieve a single category.

    Args:
        category_id: Primary key of the category.
        service: Injected CategoryService.

    Returns:
        The requested CategoryResponse.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    return await service.get_by_id(category_id)  # type: ignore[return-value] — service returns Category ORM, FastAPI serialises to CategoryResponse


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a category",
    description="Applies partial updates to an existing category.",
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    """Update an existing category.

    Args:
        category_id: Primary key of the category.
        payload: Validated update payload.
        service: Injected CategoryService.

    Returns:
        The updated CategoryResponse.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    return await service.update(category_id, payload)  # type: ignore[return-value] — service returns Category ORM, FastAPI serialises to CategoryResponse


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    description="Deletes a category by its ID. Associated todos will have category_id set to null.",
)
async def delete_category(
    category_id: int,
    service: Annotated[CategoryService, Depends(get_category_service)],
) -> None:
    """Delete a category.

    Args:
        category_id: Primary key of the category to delete.
        service: Injected CategoryService.

    Raises:
        HTTPException: 404 if the category does not exist.
    """
    await service.delete(category_id)
