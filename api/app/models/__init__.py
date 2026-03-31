from app.models.base import Base
from app.models.todo import Todo

# Exporting all models here ensures Alembic's autogenerate picks them up
# when it imports app.models in alembic/env.py.
__all__ = ["Base", "Todo"]
