from typing import Optional

from langchain_community.chat_models import ChatOpenAI
from app.core.config import settings
from app.services.rag_agent.prompts.chatbot import CHATBOT_PROMPT

class Chatbot:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct:free",
            base_url=settings.base_url,
            api_key=settings.openrouter_api_key
        )
        self.prompt = CHATBOT_PROMPT

    async def run(self, context: list[str], history: list[str], user_query: str, summary: Optional[str] = None) -> str:
        messages = self.prompt.format_messages(
            context=context,
            history=history,
            summary=summary or "",
            user_query=user_query
        )
        response = await self.llm.ainvoke(messages)
        return response.content
