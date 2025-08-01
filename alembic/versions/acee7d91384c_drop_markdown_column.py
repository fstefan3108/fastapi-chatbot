"""drop markdown column

Revision ID: acee7d91384c
Revises: 47e941036492
Create Date: 2025-07-24 04:23:02.997443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acee7d91384c'
down_revision: Union[str, Sequence[str], None] = '47e941036492'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('websites', 'embedding')
    pass


def downgrade() -> None:
    op.add_column('websites', sa.Column('embedding', sa.TEXT, nullable=True))
    pass
