"""Rename metadata to chunk_metadata

Revision ID: 4b6ed877513b
Revises: d5b7ec76ae64
Create Date: 2025-07-24 06:04:56.059835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6ed877513b'
down_revision: Union[str, Sequence[str], None] = 'd5b7ec76ae64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: rename markdown to embedding"""
    op.alter_column('embeddings', 'metadata', new_column_name='chunk_metadata')

def downgrade() -> None:
    """Downgrade schema: rename embedding back to markdown"""
    op.alter_column('embeddings', 'chunk_metadata', new_column_name='metadata')
