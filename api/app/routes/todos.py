import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.category import CategoryRepository
from app.repositories.todo import TodoRepository
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.services.todo import TodoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


def get_todo_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TodoRepository:
    """Provide a TodoRepository for the current request.

    Args:
        session: Injected async database session.

    Returns:
        TodoRepository bound to the session.
    """
    return TodoRepository(session)


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


def get_todo_service(
    repository: Annotated[TodoRepository, Depends(get_todo_repository)],
    category_repository: Annotated[CategoryRepository, Depends(get_category_repository)],
) -> TodoService:
    """Provide a TodoService for the current request.

    Args:
        repository: Injected TodoRepository.
        category_repository: Injected CategoryRepository.

    Returns:
        TodoService bound to the repositories.
    """
    return TodoService(repository, category_repository)


@router.get(
    "",
    response_model=list[TodoResponse],
    status_code=status.HTTP_200_OK,
    summary="List all todos",
    description="Returns all todos ordered by created_at descending.",
)
async def list_todos(
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> list[TodoResponse]:
    """List all todos.

    Args:
        service: Injected TodoService.

    Returns:
        List of TodoResponse objects.
    """
    return await service.get_all()


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
    description="Creates a new todo item with the provided title and optional description.",
)
async def create_todo(
    payload: TodoCreate,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> TodoResponse:
    """Create a new todo.

    Args:
        payload: Validated create payload.
        service: Injected TodoService.

    Returns:
        The created TodoResponse.
    """
    return await service.create(payload)


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a todo by ID",
    description="Returns a single todo by its ID.",
)
async def get_todo(
    todo_id: int,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> TodoResponse:
    """Retrieve a single todo.

    Args:
        todo_id: Primary key of the todo.
        service: Injected TodoService.

    Returns:
        The requested TodoResponse.

    Raises:
        HTTPException: 404 if the todo does not exist.
    """
    return await service.get_by_id(todo_id)


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a todo",
    description="Applies partial updates to an existing todo.",
)
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> TodoResponse:
    """Update an existing todo.

    Args:
        todo_id: Primary key of the todo.
        payload: Validated update payload.
        service: Injected TodoService.

    Returns:
        The updated TodoResponse.

    Raises:
        HTTPException: 404 if the todo does not exist.
    """
    return await service.update(todo_id, payload)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
    description="Deletes a todo by its ID.",
)
async def delete_todo(
    todo_id: int,
    service: Annotated[TodoService, Depends(get_todo_service)],
) -> None:
    """Delete a todo.

    Args:
        todo_id: Primary key of the todo to delete.
        service: Injected TodoService.

    Raises:
        HTTPException: 404 if the todo does not exist.
    """
    await service.delete(todo_id)
