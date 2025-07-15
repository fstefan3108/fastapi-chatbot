from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column
from app.db.base import Base

# Website DB Model #

class Website(Base):
    __tablename__ = 'websites'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    chunks: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Website id={self.id}> title={self.title} url={self.url}>"