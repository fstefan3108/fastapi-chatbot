"""change dimension size to 1024

Revision ID: 040700c4b74a
Revises: b38d3897ed06
Create Date: 2025-09-02 19:15:48.640956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '040700c4b74a'
down_revision: Union[str, Sequence[str], None] = 'b38d3897ed06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: reset embedding column to 1024 dimensions."""
    op.drop_column('embeddings', 'embedding')
    op.add_column(
        'embeddings',
        sa.Column('embedding', Vector(1024), nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema: revert embedding column back to 384 dimensions."""
    op.drop_column('embeddings', 'embedding')
    op.add_column(
        'embeddings',
        sa.Column('embedding', Vector(384), nullable=False)
    )
