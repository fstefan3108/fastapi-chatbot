"""Change chunks column from string to JSONB

Revision ID: 4af6665319d5
Revises: 4b88ffa0efaf
Create Date: 2025-06-22 22:19:01.663066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4af6665319d5'
down_revision: Union[str, Sequence[str], None] = '4b88ffa0efaf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('websites', 'chunks')

    op.add_column("websites", sa.Column("chunks", postgresql.JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("websites", "chunks")

    op.add_column("websites", sa.Column("chunks", sa.String, nullable=True))
