"""Service layer for the Todo domain.

Responsibilities:
  - Orchestrate calls to TodoRepository.
  - Own the transaction boundary: commit after successful writes.
  - Raise HTTPException for all business-rule violations (not-found, etc.).
  - Convert ORM instances to Pydantic response schemas before returning.

The service intentionally has no knowledge of SQL — all DB access goes
through the repository.
"""

import logging

from fastapi import HTTPException

from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import CreateTodoRequest, TodoResponse, UpdateTodoRequest

logger = logging.getLogger(__name__)


class TodoService:
    """Business-logic handler for Todo operations."""

    def __init__(self, repository: TodoRepository) -> None:
        """Bind the service to an already-initialised repository.

        Args:
            repository: A TodoRepository whose session is ready for use.
        """
        self.repository = repository

    async def get_all_todos(self) -> list[TodoResponse]:
        """Retrieve every Todo, newest first.

        Returns:
            A (possibly empty) list of TodoResponse objects.
        """
        todos = await self.repository.get_all()
        return [TodoResponse.model_validate(t) for t in todos]

    async def get_todo_by_id(self, todo_id: int) -> TodoResponse:
        """Retrieve a single Todo by its id.

        Args:
            todo_id: Primary key of the desired Todo.

        Raises:
            HTTPException 404: If no Todo with that id exists.

        Returns:
            The matching TodoResponse.
        """
        todo = await self.repository.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        return TodoResponse.model_validate(todo)

    async def create_todo(self, data: CreateTodoRequest) -> TodoResponse:
        """Create a new Todo and persist it.

        Args:
            data: Validated payload from the request body.

        Returns:
            The newly created TodoResponse with DB-generated fields.
        """
        todo = await self.repository.create(
            title=data.title,
            description=data.description,
        )
        # Commit here — repository only flushes within the open transaction
        await self.repository.session.commit()
        logger.info("Created todo id=%d title=%r", todo.id, todo.title)
        return TodoResponse.model_validate(todo)

    async def update_todo(
        self, todo_id: int, data: UpdateTodoRequest
    ) -> TodoResponse:
        """Partially update an existing Todo.

        Only fields present in the request payload are changed;
        omitted fields keep their current DB values.

        Args:
            todo_id: Primary key of the Todo to update.
            data:    Validated partial-update payload.

        Raises:
            HTTPException 404: If no Todo with that id exists.

        Returns:
            The updated TodoResponse.
        """
        todo = await self.repository.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )

        # exclude_unset=True ensures only explicitly supplied fields are updated
        updates = data.model_dump(exclude_unset=True)
        todo = await self.repository.update(todo, **updates)
        await self.repository.session.commit()
        logger.info("Updated todo id=%d fields=%s", todo_id, list(updates.keys()))
        return TodoResponse.model_validate(todo)

    async def delete_todo(self, todo_id: int) -> None:
        """Delete a Todo by its id.

        Args:
            todo_id: Primary key of the Todo to delete.

        Raises:
            HTTPException 404: If no Todo with that id exists.
        """
        todo = await self.repository.get_by_id(todo_id)
        if todo is None:
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        await self.repository.delete(todo)
        await self.repository.session.commit()
        logger.info("Deleted todo id=%d", todo_id)
