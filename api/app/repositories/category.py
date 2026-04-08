import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryRepository:
    """Handles all SQLAlchemy queries for the categories table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Category]:
        """Return all categories ordered by name ascending.

        Returns:
            List of Category ORM objects.
        """
        result = await self.session.execute(
            select(Category).order_by(Category.name.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, category_id: int) -> Category | None:
        """Return a single category by primary key, or None if not found.

        Args:
            category_id: Primary key of the category.

        Returns:
            Category ORM object or None.
        """
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Category | None:
        """Return a single category by name (case-sensitive), or None if not found.

        Args:
            name: Exact name to search for.

        Returns:
            Category ORM object or None.
        """
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalars().first()

    async def create(self, data: CategoryCreate) -> Category:
        """Persist a new category and flush to obtain its ID.

        Args:
            data: Validated create payload.

        Returns:
            The newly created Category ORM object (before commit).
        """
        category = Category(**data.model_dump())
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: Category, data: CategoryUpdate) -> Category:
        """Apply partial updates to an existing category and flush.

        Args:
            category: Existing Category ORM object.
            data: Validated update payload (only non-None fields applied).

        Returns:
            The updated Category ORM object (before commit).
        """
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(category, field, value)
        await self.session.flush()
        return category

    async def delete(self, category: Category) -> None:
        """Delete an existing category and flush.

        Args:
            category: Existing Category ORM object to delete.
        """
        await self.session.delete(category)
        await self.session.flush()
