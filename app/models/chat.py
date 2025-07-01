import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Chat(Base):
    __tablename__ = "chat_histories"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)
    message = Column(String, nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    website_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)