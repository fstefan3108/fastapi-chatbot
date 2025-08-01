import uuid
from fastapi import APIRouter
from starlette import status
from app.api.deps import db_dependency, api_key_dependency
from app.schemas.chat import ChatRequest, FullChatResponse, ChatResponse
from app.schemas.session import SessionResponse
from app.services.chat.chatbot_session import ChatBotSession

router = APIRouter()

@router.post("/session", status_code=status.HTTP_201_CREATED, response_model=SessionResponse)
async def create_session():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@router.post("/chat", status_code=status.HTTP_201_CREATED, response_model=FullChatResponse)
async def create_chat_and_reply(chat: ChatRequest, db: db_dependency, website: api_key_dependency):
    chatbot_session = ChatBotSession(db=db, chat=chat, website=website)
    user_message, assistant_reply = await chatbot_session.generate_and_store_reply()
    return FullChatResponse(
        user_message = ChatResponse.model_validate(user_message),
        assistant_reply = ChatResponse.model_validate(assistant_reply)
    )