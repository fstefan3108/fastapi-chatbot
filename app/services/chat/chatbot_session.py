from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models import Chat, Website
from app.schemas.chat import ChatRequest
from app.services.agents.chatbot import DeepseekChatbot
from app.services.agents.overseer import Overseer
from app.services.chat.service import ChatService
from app.services.embedding.service import EmbeddingService
from app.utils.format_chat import format_chat_history

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
        self.chat_service = ChatService(db=db, website_id=self.website.id)
        self.embedding_service = EmbeddingService(db=db, website_id=self.website.id)

    async def generate_context(self) -> tuple[str, Any]:

        try:
            chat_history = await self.chat_service.get_chat_history(session_id=self.chat.session_id)
            logger.info("[SUCCESS] Created chat history")

            formatted_history = format_chat_history(chat_history)
            logger.info(f"CHAT HISTORY: {formatted_history}")

            overseer = Overseer(history=formatted_history, user_prompt=self.chat.message)
            search_plan = await overseer.run_agent()
            logger.info(f"[SUCCESS] Overseer generated a search plan: {search_plan}")

            context = await self.embedding_service.hybrid_search(search_plan=search_plan)
            logger.info(f"Final context: {context}")

            return context, formatted_history

        except Exception as e:
            logger.error(f"[ERROR] {e}")
            raise

    async def generate_and_store_reply(self) -> tuple[Chat, Chat]:
        try:
            full_context, formatted_history = await self.generate_context()

            deepseek_chatbot = DeepseekChatbot(context=full_context, history=formatted_history, current_prompt=self.chat.message)
            deepseek_reply = await deepseek_chatbot.run_agent()
            logger.info("[SUCCESS] Deepseek generated a reply")

            user_message = await self.chat_service.create_user_prompt(chat=self.chat)
            logger.info(f"[SUCCESS] Created new user prompt")

            assistant_reply = await self.chat_service.create_assistant_reply(session_id=self.chat.session_id, reply=deepseek_reply.response)
            logger.info("[SUCCESS] Deepseek's reply stored in database")

            return user_message, assistant_reply

        except Exception as e:
            logger.error(f"[ERROR] {e}")
            raise






