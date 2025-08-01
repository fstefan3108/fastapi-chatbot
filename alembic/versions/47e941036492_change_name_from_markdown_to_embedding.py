"""Change name from markdown to embedding

Revision ID: 47e941036492
Revises: 0aab8baf44f6
Create Date: 2025-07-23 04:41:12.699913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47e941036492'
down_revision: Union[str, Sequence[str], None] = '0aab8baf44f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: rename markdown to embedding"""
    op.alter_column('websites', 'markdown', new_column_name='embedding')

def downgrade() -> None:
    """Downgrade schema: rename embedding back to markdown"""
    op.alter_column('websites', 'embedding', new_column_name='markdown')
