from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models import Chat, Website
from app.schemas.chat import ChatRequest
from app.services.chat.service import ChatService
from app.services.embedding.service import EmbeddingService
from app.utils.format_chat import format_chat_history
from app.services.parse.parse_content import parse_with_deepseek


class ChatBotSession:

    """
    - Class for creating the ChatBot session workflow
    - generate_context() -> creates the context for the chatbot by getting embeddings and chat history
    - this will now be generated before the user prompts the chatbot, drastically improving response speed.
    - generate_deepseek_response() -> prompts deepseek and returns its reply
    - store_message() -> Stores both the user's prompt and deepseek's reply in the database.
    """

    def __init__(self, db: AsyncSession, chat: ChatRequest, website: Website):
        self.db = db
        self.website = website
        self.chat = chat
        self.chat_service = ChatService(db=db, website=website)
        self.embedding_service = EmbeddingService(db=db, website_id=website.id)

    async def generate_context(self) -> tuple[str, Any]:

        try:
            context = await self.embedding_service.hybrid_search(self.chat.message)
            logger.info(f"FULL CONTEXT: {context}")

            chat_history = await self.chat_service.get_chat_history(chat=self.chat)
            logger.info("[SUCCESS] Created chat history")

            formatted_history = format_chat_history(chat_history)
            logger.info(f"CHAT HISTORY: {formatted_history}")
            return context, formatted_history

        except Exception as e:
            logger.error(f"[ERROR] {e}")
            raise

    async def generate_and_store_reply(self) -> tuple[Chat, Chat]:
        try:
            full_context, formatted_history = await self.generate_context()

            deepseek_reply = await parse_with_deepseek(context=full_context, history=formatted_history, current_prompt=self.chat.message)
            logger.info("[SUCCESS] Deepseek generated a reply")

            user_message = await self.chat_service.create_user_prompt(chat=self.chat)
            logger.info(f"[SUCCESS] Created new user prompt")

            assistant_reply = await self.chat_service.create_deepseek_reply(chat=self.chat, reply=deepseek_reply)
            logger.info("[SUCCESS] Deepseek's reply stored in database")

            return user_message, assistant_reply

        except Exception as e:
            logger.error(f"[ERROR] {e}")
            raise






