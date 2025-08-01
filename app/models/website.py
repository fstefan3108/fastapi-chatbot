import secrets
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.db.base import Base

# Website DB Model #

class Website(Base):
    __tablename__ = 'websites'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    api_key: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        index=True,
        default=lambda: secrets.token_urlsafe(32) # Generates a unique key foreach row every time the row is created #
    )

    def __repr__(self) -> str:
        return f"<Website id={self.id}> title={self.title} url={self.url}>"