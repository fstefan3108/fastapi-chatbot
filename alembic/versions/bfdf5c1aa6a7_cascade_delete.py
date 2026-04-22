"""cascade_delete

Revision ID: bfdf5c1aa6a7
Revises: 040700c4b74a
Create Date: 2025-09-04 03:01:56.311658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfdf5c1aa6a7'
down_revision: Union[str, Sequence[str], None] = '040700c4b74a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop existing foreign key constraints
    op.drop_constraint('embeddings_website_id_fkey', 'embeddings', type_='foreignkey')
    op.drop_constraint('fk_chat_histories_website_id', 'chat_histories', type_='foreignkey')

    # Add foreign key constraints with CASCADE
    op.create_foreign_key(
        'fk_embeddings_website_id',
        'embeddings', 'websites',
        ['website_id'], ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'fk_chat_histories_website_id',
        'chat_histories', 'websites',
        ['website_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade():
    # Drop CASCADE foreign key constraints
    op.drop_constraint('fk_embeddings_website_id', 'embeddings', type_='foreignkey')
    op.drop_constraint('fk_chat_histories_website_id', 'chat_histories', type_='foreignkey')

    # Restore original foreign key constraints without CASCADE
    op.create_foreign_key(
        'fk_embeddings_website_id',
        'embeddings', 'websites',
        ['website_id'], ['id']
    )

    op.create_foreign_key(
        'fk_chat_histories_website_id',
        'chat_histories', 'websites',
        ['website_id'], ['id']
    )
