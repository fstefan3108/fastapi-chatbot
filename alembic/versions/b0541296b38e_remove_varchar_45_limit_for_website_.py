"""Remove varchar(45) limit for website title

Revision ID: b0541296b38e
Revises: fd732aed3d77
Create Date: 2025-07-14 23:12:19.225979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0541296b38e'
down_revision: Union[str, Sequence[str], None] = 'fd732aed3d77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'websites',
        'title',
        existing_type=sa.VARCHAR(length=45),
        type_=sa.Text(),
        existing_nullable=False
    )
    pass


def downgrade() -> None:
    op.alter_column(
        'websites',
        'title',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=45),
        existing_nullable=False
    )
    pass
