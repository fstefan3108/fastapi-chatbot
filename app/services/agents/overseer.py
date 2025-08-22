from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from app.schemas.overseer import SearchPlan

class Overseer:
    """
    The overseer agent responsbile for formatting RAG search queries for the semantic and full text search,
    and deciding whether or not a text to sql query search would be more aplicable.
    - history -> full conversation for this/that session.
    - user_prompt -> the user's question, which is then formatted by the overseer.
    - model -> defines the model the Agent() will use.
    - instructions -> creates the specific task instructions.
    """
    def __init__(self, history: list[dict], user_prompt: str):
        self.history = history
        self.user_prompt = user_prompt
        self.model = OpenAIModel(
            "openrouter/horizon-beta",
            provider="openrouter"
        )

        instructions = self._get_instructions()
        self.overseer_llm = Agent(
            model=self.model,
            system_prompt="""
You are an AI assistant responsible for preparing queries for a hybrid retrieval system. Your task is to analyze the conversation history and the user's latest question, and generate two types of queries:

1. A **semantic search query** — a natural language question or statement that clearly reflects the user’s intent and can be embedded and compared semantically.

2. A **keyword search query** — a list of keyword groups for full-text search, where each inner list represents a set of keywords that should appear together in a document. These are used in boolean-style search engines (e.g. Postgres full-text search).

You MUST return a structured JSON object matching the following Pydantic model:

```python
class RagQueries(BaseModel):
    semantic: str
    keyword: list[list[str]]

    class OverseerSearchPlan(BaseModel):
        rag_queries: RagQueries
        """,
            output_type=SearchPlan,
            instructions=instructions,
        )

    async def run_agent(self) -> SearchPlan:
        try:
            result = await self.overseer_llm.run()
            return result.output
        except Exception as e:
            print(f"Error running overseer: {e}")
            raise e

    def _get_instructions(self) -> str:
        return f"""
Conversation so far:
        {self.history}

Latest user question:
        {self.user_prompt}

Your task is to reformulate the question and return semantic and keyword queries.
"""
