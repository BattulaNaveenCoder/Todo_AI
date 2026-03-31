"""Pydantic v2 schemas for the Todo domain.

Separation of concerns:
  - TodoResponse   : outbound shape returned to the client.
  - CreateTodoRequest : inbound payload for POST /todos.
  - UpdateTodoRequest : inbound payload for PATCH /todos/{id}
                        (all fields optional — partial update).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoResponse(BaseModel):
    """Schema returned to the client for every Todo read operation.

    ``from_attributes=True`` allows Pydantic to read values from
    SQLAlchemy ORM instances directly (replaces the old orm_mode).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class CreateTodoRequest(BaseModel):
    """Payload required to create a new Todo.

    ``title`` is mandatory and must be between 1 and 255 characters.
    ``description`` is optional.
    """

    title: str = Field(..., min_length=1, max_length=255, description="Todo title")
    description: str | None = Field(
        default=None, description="Optional extended description"
    )


class UpdateTodoRequest(BaseModel):
    """Payload for partially updating an existing Todo.

    Every field is optional — only supplied fields are altered.
    This enables PATCH semantics without requiring the full object.
    """

    title: str | None = Field(
        default=None, min_length=1, max_length=255, description="New title"
    )
    description: str | None = Field(
        default=None, description="New description (pass null to clear)"
    )
    is_completed: bool | None = Field(
        default=None, description="Toggle completion state"
    )
