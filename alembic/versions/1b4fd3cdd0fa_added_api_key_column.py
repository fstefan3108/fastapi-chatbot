"""Added api_key Column

Revision ID: 1b4fd3cdd0fa
Revises: f9d306c3d3c2
Create Date: 2025-07-29 05:17:00.160240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4fd3cdd0fa'
down_revision: Union[str, Sequence[str], None] = 'f9d306c3d3c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "websites",
        sa.Column("api_key", sa.String(length=64), nullable=False)
    )
    op.create_index("websites_api_key", "websites", ["api_key"], unique=True)

def downgrade() -> None:
    op.drop_index("ix_websites_api_key", table_name="websites")
    op.drop_column("websites", "api_key")
