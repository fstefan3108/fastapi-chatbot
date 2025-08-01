import uuid
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, TIMESTAMP, func, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Chat(Base):
    __tablename__ = "chat_histories"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    website_id: Mapped[int] = mapped_column(Integer, ForeignKey("websites.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    Index("chat_history_session_timestamp", "session_id", "timestamp")

    def __repr__(self) -> str:
        return f"<Chat id={self.id} role={self.role} session_id={self.session_id}>"