"""Added chat_histories table

Revision ID: 671e80b8e14d
Revises: 4af6665319d5
Create Date: 2025-06-27 00:35:23.955119

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '671e80b8e14d'
down_revision: Union[str, Sequence[str], None] = '4af6665319d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chat_histories',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column('website_id', sa.Integer, sa.ForeignKey("websites.id", ondelete="CASCADE"), nullable=False),
        sa.Column('session_id', sa.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('message', sa.String, nullable=False),
        sa.Column('role', sa.String, nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant')", name="check_chat_role_valid")
    )




def downgrade() -> None:
    op.drop_table('chat_histories')
