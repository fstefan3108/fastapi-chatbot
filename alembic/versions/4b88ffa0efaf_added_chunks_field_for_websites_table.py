"""Added Chunks field for websites table

Revision ID: 4b88ffa0efaf
Revises: 
Create Date: 2025-06-21 03:28:15.621907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b88ffa0efaf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("websites", sa.Column("chunks", sa.String, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
