from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CategoryBase(BaseModel):
    """Shared fields for Category schemas."""

    name: str = Field(..., min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category. All fields optional."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str | None = Field(None, min_length=1, max_length=100)


class CategoryResponse(CategoryBase):
    """Schema for serialising a category in API responses."""

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime
