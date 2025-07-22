"""Column namge change from chunks to markdown

Revision ID: fa72c2997c7b
Revises: b0541296b38e
Create Date: 2025-07-22 03:56:24.565235

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fa72c2997c7b'
down_revision: Union[str, Sequence[str], None] = 'b0541296b38e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('websites', 'chunks', new_column_name='markdown')

def downgrade() -> None:
    op.alter_column('websites', 'markdown', new_column_name='chunks')
