from pydantic import BaseModel
from uuid import UUID

class SessionResponse(BaseModel):
    session_id: UUID