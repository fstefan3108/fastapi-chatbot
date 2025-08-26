from langchain_community.chat_models import ChatOpenAI
from app.core.config import settings
from app.services.rag_agent.prompts.summarizer import SUMMARIZER_PROMPT

class Summarizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct:free",
            base_url = settings.base_url,
            api_key = settings.openrouter_api_key
        )
        self.prompt = SUMMARIZER_PROMPT

    async def run(self, history: list[str]) -> str:
        messages = self.prompt.format_messages(chat_history=history)
        result = await self.llm.ainvoke(messages)

        return result.content