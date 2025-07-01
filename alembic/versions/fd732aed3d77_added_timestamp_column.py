"""Added timestamp column

Revision ID: fd732aed3d77
Revises: 671e80b8e14d
Create Date: 2025-06-27 01:52:09.131225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP

# revision identifiers, used by Alembic.
revision: str = 'fd732aed3d77'
down_revision: Union[str, Sequence[str], None] = '671e80b8e14d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("chat_histories", sa.Column("timestamp", TIMESTAMP(timezone=True), server_default=func.now(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("chat_histories", "timestamp")
    pass
