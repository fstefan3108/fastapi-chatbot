import uuid
from fastapi import APIRouter
from app.api.deps import user_dependency, db_dependency
from app.schemas.chat import ChatRequest
from app.services.chat.handle_chat import handle_chat

router = APIRouter()

@router.post("/chat", status_code=201)
async def create_chat(user: user_dependency, db: db_dependency, chat: ChatRequest):
    deepseek_response = handle_chat(db=db, chat=chat, user=user)
    return {"response": deepseek_response}


@router.post("/session", status_code=201)
async def create_session():
    session_id = uuid.uuid4()
    return {"session_id": session_id}
