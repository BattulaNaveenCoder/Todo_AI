"""create_categories_table

Revision ID: 420e2096bbc2
Revises: fc2c2f664c81
Create Date: 2026-04-08 14:12:46.270277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '420e2096bbc2'
down_revision: Union[str, None] = 'fc2c2f664c81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
