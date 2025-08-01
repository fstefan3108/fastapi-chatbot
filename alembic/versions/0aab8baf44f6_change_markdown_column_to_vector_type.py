"""Change markdown column to vector type


Revision ID: 0aab8baf44f6
Revises: fa72c2997c7b
Create Date: 2025-07-23 04:25:37.756123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0aab8baf44f6'
down_revision: Union[str, Sequence[str], None] = 'fa72c2997c7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("websites", "markdown")
    op.execute("ALTER TABLE websites ADD COLUMN markdown vector(384)")

def downgrade() -> None:
    op.drop_column("websites", "markdown")
    op.add_column("websites", sa.Column("markdown", sa.dialects.postgresql.JSONB, nullable=False))
