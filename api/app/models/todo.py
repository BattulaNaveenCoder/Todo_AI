"""SQLAlchemy ORM model for the Todo entity."""

import logging
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

logger = logging.getLogger(__name__)


class Todo(Base):
    """Represents a single todo item in the database.

    Columns:
        id          -- Auto-incremented primary key.
        title       -- Short, required description (max 255 chars).
        description -- Optional long-form text.
        is_completed-- Completion flag; defaults to False.
        created_at  -- Set by the DB server on INSERT.
        updated_at  -- Set by the DB server on INSERT; updated on every UPDATE.
    """

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # server_default lets the DB engine assign the timestamp — avoids clock skew
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    # onupdate triggers a new timestamp every time the row is modified
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a developer-friendly representation of this Todo."""
        return f"<Todo id={self.id} title={self.title!r} completed={self.is_completed}>"
