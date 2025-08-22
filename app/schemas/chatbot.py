from pydantic import Field, BaseModel

class ChatbotAnswer(BaseModel):
    response: str = Field(description="Direct and concise answer to the user's question, based solely on the provided website content")