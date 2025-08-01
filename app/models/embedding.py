from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base

# Website DB Model #

class Embeddings(Base):
    __tablename__ = 'embeddings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chunk: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    website_id: Mapped[int] = mapped_column(Integer, ForeignKey('websites.id'), nullable=False, index=True)
    fts_vector: Mapped[str] = mapped_column(TSVECTOR)

    def __repr__(self) -> str:
        return f"<Embedding id={self.id}> chunk={self.chunk} website_id={self.website_id}>"