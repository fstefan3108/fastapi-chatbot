from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.schemas.chat import ChatRequest
from app.services.chat.service import ChatService
from app.utils.format_chat import format_chat_history
from app.services.parse.parse_content import parse_with_deepseek
from app.utils.db_transaction import db_transactional_async
from app.vectorstore.get_embeddings import get_embeddings


class ChatBotSession:

    """
    - Class for creating the ChatBot session workflow
    - generate_context() -> creates the context for the chatbot by getting embeddings and chat history
    - this will now be generated before the user prompts the chatbot, drastically improving response speed.
    - generate_deepseek_response() -> prompts deepseek and returns its reply
    - store_message() -> Stores both the user's prompt and deepseek's reply in the database.
    """

    def __init__(self, db: AsyncSession, user: dict, chat: ChatRequest):
        self.db = db
        self.user = user
        self.user_id = user["id"]
        self.chat = chat
        self.chat_service = ChatService(db=db)

    async def generate_context(self):

        context = await get_embeddings(
            user_id=self.user_id,
            user_prompt=self.chat.message,
            website_id=self.chat.website_id
        )
        logger.info("[SUCCESS] Fetched embeddings / Stored Context")

        chat_history = await self.chat_service.get_chat_history(chat=self.chat)

        # if there's no prior history: #
        chat_history.append({
            "role": "user",
            "content": self.chat.message
        })

        formatted_history = format_chat_history(chat_history)
        logger.info("[SUCCESS] Created Chat History")
        print(formatted_history)
        return context, formatted_history


    @db_transactional_async
    async def generate_and_store_reply(self):
        context, formatted_history = await self.generate_context()

        deepseek_reply = await parse_with_deepseek(context=context, history=formatted_history)
        logger.info("[SUCCESS] Deepseek generated a reply")

        await self.chat_service.create_user_prompt(chat=self.chat, user=self.user)
        logger.info(f"[SUCCESS] Created new user prompt")

        await self.chat_service.create_deepseek_reply(chat=self.chat, user=self.user, reply=deepseek_reply)
        logger.info("[SUCCESS] Deeepseek's reply stored in database")

        return deepseek_reply






