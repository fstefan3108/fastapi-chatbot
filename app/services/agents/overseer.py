from pydantic_ai import Agent
from app.schemas.search_plan import OverseerSearchPlan
from httpx import AsyncClient
from pydantic_ai.models.openai import OpenAIModel

custom_http_client = AsyncClient(timeout=30)

import os
print("[DEBUG] DEEPSEEK_API_KEY =", os.getenv("OPENROUTER_API_KEY"))

model = OpenAIModel(
    'deepseek/deepseek-chat-v3-0324:free',
    provider='openrouter'
)

overseer_search_plan = Agent(
    model=model,
    output_type=OverseerSearchPlan,
    system_prompt="You are a helpful assistant that extracts semantic and keyword search queries from a user's conversation."
)
