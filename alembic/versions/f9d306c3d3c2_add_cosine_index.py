"""add cosine index

Revision ID: f9d306c3d3c2
Revises: 4b6ed877513b
Create Date: 2025-07-26 02:16:02.990153

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9d306c3d3c2'
down_revision: Union[str, Sequence[str], None] = '4b6ed877513b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_embeddings_cosine
        ON embeddings USING hnsw (embedding vector_cosine_ops);
    """)

def downgrade():
    op.execute("""
        DROP INDEX IF EXISTS idx_embeddings_cosine;
    """)
