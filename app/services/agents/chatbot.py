from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from app.schemas.chatbot import ChatbotAnswer

class DeepseekChatbot:
    """
    The chatbot agent responsible for answering user prompts based on provided formatted context by the overseer.
    - context -> formatted context provided by the overseer (semantic + full text search results).
    - history -> full conversation history so far in this/that session.
    - current_prompt -> user's present question.
    run_agent() -> calls PydanticAI .run() method on the agent object, returns ChatbotAnswer scheme output.
    _get_instructions() -> gets the instructions for the specific task the chatbot should perform.
    Note: Difference between system_prompt and _get_instructions():
    system_prompt field in the Agent module defines the chatbot's general role and identity, while the
    _get_instructions() method tells the agent the specific task it should perform while also passing it
    dynamic values such as context, history, etc.
    """
    def __init__(self, context: str, history: list[str], current_prompt: str):
        self.context = context
        self.history = history
        self.current_prompt = current_prompt
        instructions = self._get_instructions()
        self.model = OpenAIModel(
            "mistralai/mistral-7b-instruct",
            provider="openrouter"
        )
        self.chatbot_llm = Agent(
            model=self.model,
            system_prompt="""
You are a helpful AI assistant that answers user questions based strictly on the provided website content.

IMPORTANT RULES:
- Only use the provided website context.
- Do NOT invent answers or make assumptions.
- If the answer is not in the content, respond: "That information is not available on the website."
- Be concise and direct.
""",
            output_type=ChatbotAnswer,
            instructions=instructions,
        )

    async def run_agent(self) -> ChatbotAnswer:
        try:
            result = await self.chatbot_llm.run()
            return result.output
        except Exception as e:
            print(f"Error running Deepseek chatbot: {e}")
            raise e

    def _get_instructions(self) -> str:
        return f"""
Website content:
{self.context}

Conversation so far:
{self.history}

Latest user question:
{self.current_prompt}

Your task: Provide a clear and concise answer to the user's question using ONLY the website content above.
If the answer is not found, say: "That information is not available on the website."
"""
