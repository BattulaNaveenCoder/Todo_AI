"""Repository layer for the Todo domain.

Responsibilities:
  - All SQLAlchemy queries for the ``todos`` table.
  - No business logic, no HTTP knowledge, no exception translation.
  - Receives an ``AsyncSession`` through the constructor (injected by FastAPI).

The repository flushes after writes but does NOT commit — the Service
layer owns the transaction boundary and calls ``session.commit()``.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo

logger = logging.getLogger(__name__)


class TodoRepository:
    """Data-access object for the Todo table."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind this repository to an open database session.

        Args:
            session: The async SQLAlchemy session provided by get_db().
        """
        self.session = session

    async def get_all(self) -> list[Todo]:
        """Return all todos ordered newest-first.

        Returns:
            A list of Todo ORM instances (may be empty).
        """
        result = await self.session.execute(
            select(Todo).order_by(Todo.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, todo_id: int) -> Todo | None:
        """Fetch a single Todo by its primary key.

        Args:
            todo_id: The primary key to look up.

        Returns:
            The matching Todo or None if no row exists.
        """
        result = await self.session.execute(
            select(Todo).where(Todo.id == todo_id)
        )
        return result.scalar_one_or_none()

    async def create(self, title: str, description: str | None) -> Todo:
        """Insert a new Todo row and flush it to get the auto-generated id.

        Args:
            title:       Required title text.
            description: Optional extended description.

        Returns:
            The newly created Todo with all DB-generated fields populated.
        """
        todo = Todo(title=title, description=description)
        self.session.add(todo)

        # flush sends the INSERT to the DB within this transaction so that
        # auto-generated values (id, created_at) are available immediately
        await self.session.flush()
        await self.session.refresh(todo)
        return todo

    async def update(self, todo: Todo, **fields: object) -> Todo:
        """Apply partial field updates to an existing Todo and flush.

        Args:
            todo:    The ORM instance to mutate.
            **fields: Keyword arguments mapping column names to new values.

        Returns:
            The same Todo instance with refreshed column values.
        """
        for key, value in fields.items():
            setattr(todo, key, value)

        await self.session.flush()
        await self.session.refresh(todo)
        return todo

    async def delete(self, todo: Todo) -> None:
        """Remove a Todo row and flush the DELETE within the transaction.

        Args:
            todo: The ORM instance to delete.
        """
        await self.session.delete(todo)
        await self.session.flush()
