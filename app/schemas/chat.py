from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: UUID

class ChatResponse(BaseModel):
    role: str
    message: str
    session_id: UUID
    website_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class FullChatResponse(BaseModel):
    user_message: ChatResponse
    assistant_reply: ChatResponse

class ChatCreate(BaseModel):
    message: str
    session_id: UUID
    role: str
    website_id: int