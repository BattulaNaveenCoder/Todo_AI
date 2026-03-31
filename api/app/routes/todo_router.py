"""FastAPI route handlers for the Todo domain.

Responsibilities:
  - Define all HTTP endpoints under the /api/todos prefix.
  - Delegate all logic to TodoService — zero business rules here.
  - Return the correct HTTP status codes per operation.
  - Declare dependencies for DI chain: get_db → TodoRepository → TodoService.

Status codes used:
  200 GET list / GET by id / PATCH
  201 POST  (resource created)
  204 DELETE (no response body)
  404 not found  (raised by service)
"""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import CreateTodoRequest, TodoResponse, UpdateTodoRequest
from app.services.todo_service import TodoService

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency factories — build the DI chain for each request
# ---------------------------------------------------------------------------

def get_todo_repository(session: AsyncSession = Depends(get_db)) -> TodoRepository:
    """Create a TodoRepository bound to the current request's DB session.

    FastAPI injects the AsyncSession via get_db and passes it here.
    """
    return TodoRepository(session)


def get_todo_service(
    repository: TodoRepository = Depends(get_todo_repository),
) -> TodoService:
    """Create a TodoService with the already-constructed repository.

    Full DI chain: get_db → TodoRepository → TodoService → Route.
    """
    return TodoService(repository)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=list[TodoResponse],
    summary="List all todos",
)
async def list_todos(
    service: TodoService = Depends(get_todo_service),
) -> list[TodoResponse]:
    """Return all todos ordered by creation date (newest first)."""
    return await service.get_all_todos()


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a single todo",
)
async def get_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Return a single Todo by its primary key.

    Raises 404 if the todo does not exist.
    """
    return await service.get_todo_by_id(todo_id)


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo",
)
async def create_todo(
    payload: CreateTodoRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Create and persist a new Todo. Returns 201 with the created resource."""
    return await service.create_todo(payload)


@router.patch(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Partially update a todo",
)
async def update_todo(
    todo_id: int,
    payload: UpdateTodoRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    """Partially update a Todo — only supplied fields are changed.

    Raises 404 if the todo does not exist.
    """
    return await service.update_todo(todo_id, payload)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a todo",
)
async def delete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service),
) -> None:
    """Delete a Todo by its primary key.

    Returns 204 No Content on success.
    Raises 404 if the todo does not exist.
    """
    await service.delete_todo(todo_id)
