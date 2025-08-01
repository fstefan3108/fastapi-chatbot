"""Change website_id to FK

Revision ID: 164748c2974b
Revises: 1b4fd3cdd0fa
Create Date: 2025-07-30 05:02:25.394483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '164748c2974b'
down_revision: Union[str, Sequence[str], None] = '1b4fd3cdd0fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("chat_histories", "user_id")
    op.create_foreign_key("fk_chat_histories_website_id", "chat_histories", "websites", ['website_id'], ['id'])
    op.create_index('chat_histories_website_id', 'chat_histories', ['website_id'])
    pass


def downgrade():
    # Reverse operations
    op.drop_index('ix_chat_histories_website_id', table_name='chat_histories')
    op.drop_constraint('fk_chat_histories_website_id', 'chat_histories', type_='foreignkey')
    op.drop_column('chat_histories', 'website_id')
    op.add_column('chat_histories', sa.Column('user_id', sa.Integer(), nullable=True))
    pass
