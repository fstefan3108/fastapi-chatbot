import uuid

from fastapi import APIRouter
from app.api.deps import user_dependency, db_dependency
from app.schemas.chat import ChatRequest
from app.services.handle_chat import handle_chat
from app.utils.validation import check_user

router = APIRouter()

@router.post("/chat", status_code=201)
async def chatbot_message(user: user_dependency, db: db_dependency, chat: ChatRequest):
    check_user(user=user, status_code=404, detail="User not found.")
    deepseeks_response = handle_chat(db=db, chat=chat, user=user)

    return {"response": deepseeks_response}

@router.post("/start_session", status_code=201)
async def start_session(user: user_dependency):
    check_user(user=user, status_code=404, detail="User not found.")
    session_id = uuid.uuid4()

    return {"session_id": session_id}
