"""Migrated to LangChain table

Revision ID: 21e660fe27bf
Revises: b38d3897ed06
Create Date: 2025-08-01 05:55:05.061600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector import Vector
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision: str = '21e660fe27bf'
down_revision: Union[str, Sequence[str], None] = 'b38d3897ed06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("embeddings")
    pass


def downgrade() -> None:
    op.create_table(
        'embeddings',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('chunk', sa.Text, nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('chunk_metadata', JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column('website_id', sa.Integer, sa.ForeignKey('websites.id'), nullable=False, index=True),
        sa.Column('fts_vector', TSVECTOR)
    )
