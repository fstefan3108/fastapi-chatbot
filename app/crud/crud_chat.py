from app.api.deps import db_dependency, user_dependency
from app.crud.base import create, get_by
from app.models.chat import Chat
from app.schemas.chat import ChatRequest


def add_user_prompt(db: db_dependency, chat: ChatRequest, user: user_dependency):
    values = {
        "role": "user",
        "message": chat.message,
        "session_id": chat.session_id,
        "website_id": chat.website_id,
        "user_id": user.get("id"),
    }

    message = create(model=Chat, db=db, data=values)
    return message


def add_deepseek_reply(db: db_dependency, chat: ChatRequest, user:user_dependency, reply: str):
    values = {
        "role": "assistant",
        "message": reply,
        "session_id": chat.session_id,
        "website_id": chat.website_id,
        "user_id": user.get("id"),
    }

    deepseek_reply = create(model=Chat, db=db, data=values)
    return deepseek_reply

def get_chat_history(db: db_dependency, chat: ChatRequest):
    criteria = Chat.session_id == chat.session_id
    order = Chat.timestamp
    chat_history = get_by(model=Chat, db=db, criteria=criteria, order=order)
    return chat_history