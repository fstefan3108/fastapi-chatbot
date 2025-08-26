from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from app.core.config import settings
from app.schemas.search_plan import RagQueries, SearchPlan
from app.services.rag_agent.prompts.overseer import OVERSEER_PROMPT
from app.services.rag_agent.schemas import OverseerOutput, OverseerResponse

class Overseer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="mistralai/mistral-7b-instruct:free",
            base_url=settings.base_url,
            api_key=settings.openrouter_api_key
        )
        self.output_parser = PydanticOutputParser(pydantic_object=OverseerResponse)
        self.prompt = OVERSEER_PROMPT

    async def run(self, user_query: str, chat_history: list[str]) -> OverseerOutput:
        messages = self.prompt.format_messages(
            chat_history=chat_history,
            user_query=user_query,
            format_instructions=self.output_parser.get_format_instructions()
        )
        response = await self.llm.ainvoke(messages)

        try:
            result = self.output_parser.parse(response.content)

            return {
                "reasoning": result.reasoning,
                "formatted_query": result.formatted_query,
                "search_plan": result.search_plan
            }
        except Exception as e:
            # Fallback logic #
            print(f"[ERROR] Error occurred - using fallback logic: {e}")
            return {
                "formatted_query": user_query,
                "search_plan": SearchPlan(rag_queries=RagQueries(
                    semantic=user_query,
                    keyword=[[word] for word in user_query.split()[:3]]
                    )
                ),
                "reasoning": "Failed to parse response, using fallback"
            }
