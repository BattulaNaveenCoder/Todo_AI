import logging

from fastapi import HTTPException

from app.models.todo import Todo
from app.repositories.category import CategoryRepository
from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate

logger = logging.getLogger(__name__)


class TodoService:
    """Business logic for todo operations."""

    def __init__(
        self,
        repository: TodoRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.repository = repository
        self.category_repository = category_repository

    def _to_response(self, todo: Todo) -> TodoResponse:
        """Convert a Todo ORM object to a TodoResponse with category_name.

        Args:
            todo: Todo ORM object with category relationship loaded.

        Returns:
            TodoResponse with category_name populated.
        """
        return TodoResponse(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            is_completed=todo.is_completed,
            category_id=todo.category_id,
            category_name=todo.category.name if todo.category else None,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
        )

    async def get_all(self) -> list[TodoResponse]:
        """Return all todos.

        Returns:
            List of all TodoResponse objects ordered by created_at descending.
        """
        todos = await self.repository.get_all()
        return [self._to_response(todo) for todo in todos]

    async def get_by_id(self, todo_id: int) -> TodoResponse:
        """Return a single todo by ID, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo.

        Returns:
            The requested TodoResponse object.

        Raises:
            HTTPException: 404 if the todo does not exist.
        """
        todo = await self.repository.get_by_id(todo_id)
        if todo is None:
            logger.warning("Todo %s not found", todo_id)
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        return self._to_response(todo)

    async def _validate_category_id(self, category_id: int | None) -> None:
        """Validate that a category_id references an existing category.

        Args:
            category_id: The category ID to validate (None is always valid).

        Raises:
            HTTPException: 404 if the category does not exist.
        """
        if category_id is not None:
            category = await self.category_repository.get_by_id(category_id)
            if category is None:
                logger.warning("Category %s not found for todo assignment", category_id)
                raise HTTPException(
                    status_code=404,
                    detail=f"Category with id {category_id} not found",
                )

    async def create(self, data: TodoCreate) -> TodoResponse:
        """Create and persist a new todo.

        Args:
            data: Validated create payload.

        Returns:
            The newly created TodoResponse.

        Raises:
            HTTPException: 404 if category_id does not reference an existing category.
        """
        await self._validate_category_id(data.category_id)
        todo = await self.repository.create(data)
        await self.repository.session.commit()
        await self.repository.session.refresh(todo)
        # Re-fetch to eagerly load category relationship
        todo = await self.repository.get_by_id(todo.id)
        logger.info("Created todo id=%s title=%r", todo.id, todo.title)  # type: ignore[union-attr] — guaranteed non-None after create
        return self._to_response(todo)  # type: ignore[arg-type] — guaranteed non-None after re-fetch

    async def update(self, todo_id: int, data: TodoUpdate) -> TodoResponse:
        """Apply partial updates to a todo, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo to update.
            data: Validated update payload.

        Returns:
            The updated TodoResponse.

        Raises:
            HTTPException: 404 if the todo does not exist.
            HTTPException: 404 if category_id does not reference an existing category.
        """
        # Ensure todo exists (raises 404 if not)
        existing = await self.repository.get_by_id(todo_id)
        if existing is None:
            logger.warning("Todo %s not found", todo_id)
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        if data.category_id is not None:
            await self._validate_category_id(data.category_id)
        todo = await self.repository.update(existing, data)
        await self.repository.session.commit()
        await self.repository.session.refresh(todo)
        # Re-fetch to eagerly load category relationship
        todo = await self.repository.get_by_id(todo.id)
        logger.info("Updated todo id=%s", todo.id)  # type: ignore[union-attr] — guaranteed non-None after re-fetch
        return self._to_response(todo)  # type: ignore[arg-type] — guaranteed non-None after re-fetch

    async def delete(self, todo_id: int) -> None:
        """Delete a todo, raising 404 if not found.

        Args:
            todo_id: Primary key of the todo to delete.

        Raises:
            HTTPException: 404 if the todo does not exist.
        """
        existing = await self.repository.get_by_id(todo_id)
        if existing is None:
            logger.warning("Todo %s not found", todo_id)
            raise HTTPException(
                status_code=404, detail=f"Todo with id {todo_id} not found"
            )
        await self.repository.delete(existing)
        await self.repository.session.commit()
        logger.info("Deleted todo id=%s", todo_id)
