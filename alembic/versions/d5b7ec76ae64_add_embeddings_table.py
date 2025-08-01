"""Add embeddings table

Revision ID: d5b7ec76ae64
Revises: acee7d91384c
Create Date: 2025-07-24 04:39:51.079533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = 'd5b7ec76ae64'
down_revision: Union[str, Sequence[str], None] = 'acee7d91384c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Make sure pgvector extension is enabled
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create the embeddings table
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('chunk', sa.Text, nullable=False),
        sa.Column('embedding', Vector(dim=384), nullable=False),
        sa.Column('metadata', sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('website_id', sa.Integer, sa.ForeignKey('websites.id', ondelete='CASCADE'), nullable=False, index=True),
    )

    # Create an IVFFLAT index for similarity search using cosine distance
    op.execute("""
        CREATE INDEX embedding_cosine_idx
        ON embeddings
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS embedding_cosine_idx;")
    op.drop_table('embeddings')
    op.execute("DROP EXTENSION IF EXISTS vector")
