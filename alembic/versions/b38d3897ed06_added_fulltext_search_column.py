"""Added fulltext search column

Revision ID: b38d3897ed06
Revises: 164748c2974b
Create Date: 2025-08-01 02:46:59.950526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision: str = 'b38d3897ed06'
down_revision: Union[str, Sequence[str], None] = '164748c2974b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("embeddings", sa.Column("fts_vector", TSVECTOR))
    # Creates a GIN (Generalized Inverted Index) on the fts_vector column. #
    op.execute("CREATE INDEX fts_vector_idx ON embeddings USING GIN (fts_vector)")
    # Trigger function #
    op.execute("""
            CREATE FUNCTION embeddings_fts_trigger() RETURNS trigger AS $$
            BEGIN
                NEW.fts_vector := to_tsvector('english', NEW.chunk);
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """)
    # Bind the trigger to the table #
    op.execute("""
            CREATE TRIGGER tsvectorupdate
            BEFORE INSERT OR UPDATE ON embeddings
            FOR EACH ROW EXECUTE FUNCTION embeddings_fts_trigger();
        """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON embeddings")
    op.execute("DROP FUNCTION IF EXISTS embeddings_fts_trigger")
    op.execute("DROP INDEX IF EXISTS fts_vector_idx")
    op.drop_column('embeddings', 'fts_vector')
