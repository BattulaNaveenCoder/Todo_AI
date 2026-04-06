from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TodoBase(BaseModel):
    """Shared fields for Todo schemas."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""

    pass


class TodoUpdate(BaseModel):
    """Schema for updating an existing todo. All fields optional."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_completed: bool | None = None


class TodoResponse(TodoBase):
    """Schema for serialising a todo in API responses."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
