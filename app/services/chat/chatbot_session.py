from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models import Website
from app.schemas.chat import ChatRequest
from app.services.chat.service import ChatService
from app.services.rag_agent.workflow import Workflow

class ChatBotSession:
    """
    - Class for creating the ChatBot session workflow
    - generate_context() -> creates the context for the chatbot by getting embeddings and chat history
    - this will now be generated before the user prompts the chatbot, drastically improving response speed.
    - generate_deepseek_response() -> prompts deepseek and returns its reply
    - store_message() -> Stores both the user's prompt and deepseek's reply in the database.
    """

    def __init__(self, db: AsyncSession, website: Website):
        self.db = db
        self.website = website
        self.chat_service = ChatService(db=db, website_id=self.website.id)
        self.langgraph_workflow = Workflow(db=self.db, website_id=self.website.id)

    async def handle_chat(self, chat_request: ChatRequest):
        try:
            # Store user message to db #
            user_message = await self.chat_service.create_user_prompt(chat=chat_request)
            logger.info("[SUCCESS] User message stored to db")

            # Run langgraph workflow #
            initial_state = {
                "user_query": chat_request.message,
                "session_id": chat_request.session_id,
            }

            workflow_result = await self.langgraph_workflow.run(initial_state=initial_state)
            final_response = workflow_result.get("final_response", "")
            logger.info("[SUCCESS] Workflow completed.")

            assistant_message = await self.chat_service.create_assistant_reply(chat=chat_request, reply=final_response)
            logger.info("[SUCCESS] Assistant message stored to db")

            return user_message, assistant_message
        except Exception as e:
            logger.error(f"Chat proccessing error: {e}")
            raise



