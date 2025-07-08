from sqlalchemy.orm import Session
from app.models.chat import Chat
from app.schemas.chat import ChatRequest
from app.crud.crud_chat import crud_chat
from app.utils.db_transaction import db_transactional


class ChatService:
    def __init__(self, db: Session):
        self.db = db


    @db_transactional
    def create_user_prompt(self, chat: ChatRequest, user: dict):
        values = {
            "role": "user",
            "message": chat.message,
            "session_id": chat.session_id,
            "website_id": chat.website_id,
            "user_id": user.get("id"),
        }

        message = crud_chat.create(db=self.db, data=values)
        return message


    @db_transactional
    def create_deepseek_reply(self, chat: ChatRequest, user: dict, reply: str):
        values = {
            "role": "assistant",
            "message": reply,
            "session_id": chat.session_id,
            "website_id": chat.website_id,
            "user_id": user.get("id"),
        }

        deepseek_reply = crud_chat.create(db=self.db, data=values)
        return deepseek_reply


    def get_chat_history(self, chat: ChatRequest):
        criteria = Chat.session_id == chat.session_id
        order = Chat.timestamp
        chat_history = crud_chat.get_by(db=self.db, criteria=criteria, order=order)
        return chat_history