"""add_category_id_to_todos

Revision ID: 5a3e7c91d4f2
Revises: 420e2096bbc2
Create Date: 2026-04-08 14:13:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a3e7c91d4f2'
down_revision: Union[str, None] = '420e2096bbc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('todos', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_todos_category_id',
        'todos',
        'categories',
        ['category_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_todos_category_id', 'todos', type_='foreignkey')
    op.drop_column('todos', 'category_id')
