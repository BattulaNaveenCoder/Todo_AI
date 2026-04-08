import logging

from fastapi import HTTPException

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    """Business logic for category operations."""

    def __init__(self, repository: CategoryRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[Category]:
        """Return all categories.

        Returns:
            List of all Category objects ordered by name ascending.
        """
        return await self.repository.get_all()

    async def get_by_id(self, category_id: int) -> Category:
        """Return a single category by ID, raising 404 if not found.

        Args:
            category_id: Primary key of the category.

        Returns:
            The requested Category object.

        Raises:
            HTTPException: 404 if the category does not exist.
        """
        category = await self.repository.get_by_id(category_id)
        if category is None:
            logger.warning("Category %s not found", category_id)
            raise HTTPException(
                status_code=404, detail=f"Category with id {category_id} not found"
            )
        return category

    async def create(self, data: CategoryCreate) -> Category:
        """Create and persist a new category, raising 409 if name already exists.

        Args:
            data: Validated create payload.

        Returns:
            The newly created and refreshed Category object.

        Raises:
            HTTPException: 409 if a category with the same name already exists.
        """
        existing = await self.repository.get_by_name(data.name)
        if existing is not None:
            logger.warning("Duplicate category name=%r", data.name)
            raise HTTPException(
                status_code=409,
                detail=f"Category with name '{data.name}' already exists",
            )
        category = await self.repository.create(data)
        await self.repository.session.commit()
        await self.repository.session.refresh(category)
        logger.info("Created category id=%s name=%r", category.id, category.name)
        return category

    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        """Apply partial updates to a category, raising 404 if not found.

        Args:
            category_id: Primary key of the category to update.
            data: Validated update payload.

        Returns:
            The updated and refreshed Category object.

        Raises:
            HTTPException: 404 if the category does not exist.
            HTTPException: 409 if the updated name conflicts with another category.
        """
        category = await self.get_by_id(category_id)
        if data.name is not None and data.name != category.name:
            existing = await self.repository.get_by_name(data.name)
            if existing is not None:
                logger.warning("Duplicate category name=%r on update", data.name)
                raise HTTPException(
                    status_code=409,
                    detail=f"Category with name '{data.name}' already exists",
                )
        category = await self.repository.update(category, data)
        await self.repository.session.commit()
        await self.repository.session.refresh(category)
        logger.info("Updated category id=%s", category.id)
        return category

    async def delete(self, category_id: int) -> None:
        """Delete a category, raising 404 if not found.

        Associated todos will have category_id set to null (ON DELETE SET NULL).

        Args:
            category_id: Primary key of the category to delete.

        Raises:
            HTTPException: 404 if the category does not exist.
        """
        category = await self.get_by_id(category_id)
        await self.repository.delete(category)
        await self.repository.session.commit()
        logger.info("Deleted category id=%s", category_id)
