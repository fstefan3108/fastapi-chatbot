import uuid
from fastapi import APIRouter
from app.api.deps import user_dependency, db_dependency
from app.schemas.chat import ChatRequest
from app.services.chat.chatbot_session import ChatBotSession

router = APIRouter()

@router.post("/session", status_code=201)
async def create_session():
    session_id = uuid.uuid4()
    return {"session_id": session_id}


@router.post("/chatbot_reply", status_code=201)
async def create_chat_and_reply(user: user_dependency, db: db_dependency, chat: ChatRequest):
    chatbot_session = ChatBotSession(db=db, user=user, chat=chat)
    reply = await chatbot_session.generate_and_store_reply()
    return {"reply": reply}