from uuid import UUID

from pydantic import BaseModel



class ChatRequest(BaseModel):
    message: str
    session_id: UUID
    website_id: int