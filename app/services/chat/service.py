from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Website
from app.models.chat import Chat
from app.schemas.chat import ChatCreate, ChatRequest
from app.crud.crud_chat import crud_chat
from app.utils.db_transaction import db_transactional_async

class ChatService:
    def __init__(self, db: AsyncSession, website: Website):
        self.db = db
        self.website = website

    @db_transactional_async
    async def create_user_prompt(self, chat: ChatRequest) -> Chat:
        chat_data = chat.model_dump()
        chat_data.update({
            "role": "user",
            "website_id": self.website.id,
        })
        chat_create = ChatCreate(**chat_data)
        message = await crud_chat.create(db=self.db, data=chat_create.model_dump())
        return message

    @db_transactional_async
    async def create_deepseek_reply(self, chat: ChatRequest, reply: str) -> Chat:
        chat_data = chat.model_dump()
        chat_data.update({
            "role": "assistant",
            "message": reply,
            "website_id": self.website.id,
        })
        chat_create = ChatCreate(**chat_data)
        deepseek_reply = await crud_chat.create(db=self.db, data=chat_create.model_dump())
        return deepseek_reply


    async def get_chat_history(self, chat: ChatRequest) -> list[Chat]:
        chat_history = await crud_chat.get_all(
            db=self.db,
            criteria=Chat.session_id == chat.session_id,
            order=Chat.timestamp
        )
        return chat_history