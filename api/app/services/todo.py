import logging

from fastapi import HTTPException

from app.models.todo import Todo
from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoUpdate

logger = logging.getLogger(__name__)


class TodoService:
    """Business logic for todo operations."""

    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    async def get_all(self) -> list[Todo]:
        """Return all todos.

        Returns:
            List of all Todo objects ordered by created_at descending.
        """
        return await self.repository.get_all()

    async def get_by_id(self, todo_id: int) -> Todo:
        """Return a single todo by ID, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo.

        Returns:
            The requested Todo object.

        Raises:
            HTTPException: 404 if the todo does not exist.
        """
        todo = await self.repository.get_by_id(todo_id)
        if todo is None:
            logger.warning("Todo %s not found", todo_id)
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        return todo

    async def create(self, data: TodoCreate) -> Todo:
        """Create and persist a new todo.

        Args:
            data: Validated create payload.

        Returns:
            The newly created and refreshed Todo object.
        """
        todo = await self.repository.create(data)
        await self.repository.session.commit()
        await self.repository.session.refresh(todo)
        logger.info("Created todo id=%s title=%r", todo.id, todo.title)
        return todo

    async def update(self, todo_id: int, data: TodoUpdate) -> Todo:
        """Apply partial updates to a todo, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo to update.
            data: Validated update payload.

        Returns:
            The updated and refreshed Todo object.

        Raises:
            HTTPException: 404 if the todo does not exist.
        """
        todo = await self.get_by_id(todo_id)
        todo = await self.repository.update(todo, data)
        await self.repository.session.commit()
        await self.repository.session.refresh(todo)
        logger.info("Updated todo id=%s", todo.id)
        return todo

    async def delete(self, todo_id: int) -> None:
        """Delete a todo, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo to delete.

        Raises:
            HTTPException: 404 if the todo does not exist.
        """
        todo = await self.get_by_id(todo_id)
        await self.repository.delete(todo)
        await self.repository.session.commit()
        logger.info("Deleted todo id=%s", todo_id)
