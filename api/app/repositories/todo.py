import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoUpdate

logger = logging.getLogger(__name__)


class TodoRepository:
    """Handles all SQLAlchemy queries for the todos table."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Todo]:
        """Return all todos ordered by created_at descending.

        Returns:
            List of Todo ORM objects.
        """
        result = await self.session.execute(
            select(Todo).order_by(Todo.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, todo_id: int) -> Todo | None:
        """Return a single todo by primary key, or None if not found.

        Args:
            todo_id: Primary key of the todo.

        Returns:
            Todo ORM object or None.
        """
        result = await self.session.execute(select(Todo).where(Todo.id == todo_id))
        return result.scalars().first()

    async def create(self, data: TodoCreate) -> Todo:
        """Persist a new todo and flush to obtain its ID.

        Args:
            data: Validated create payload.

        Returns:
            The newly created Todo ORM object (before commit).
        """
        todo = Todo(**data.model_dump(), is_completed=False)
        self.session.add(todo)
        await self.session.flush()
        return todo

    async def update(self, todo: Todo, data: TodoUpdate) -> Todo:
        """Apply partial updates to an existing todo and flush.

        Args:
            todo: Existing Todo ORM object.
            data: Validated update payload (only non-None fields applied).

        Returns:
            The updated Todo ORM object (before commit).
        """
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(todo, field, value)
        await self.session.flush()
        return todo

    async def delete(self, todo: Todo) -> None:
        """Delete an existing todo and flush.

        Args:
            todo: Existing Todo ORM object to delete.
        """
        await self.session.delete(todo)
        await self.session.flush()
