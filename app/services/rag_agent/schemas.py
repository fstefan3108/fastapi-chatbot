from typing import TypedDict, Optional, Literal
from pydantic import BaseModel, Field
from app.schemas.search_plan import SearchPlan

# Pydantic AI structured response #
class OverseerResponse(BaseModel):
    # This is the output when the overseer is called, this populates the main State. #
    route: Literal["generic", "website_related"] = Field(default="Route decision for chatbot response")
    reasoning: str = Field(description="Brief explanation of search strategy")
    formatted_query: str = Field(description="Cleaned and optimized user query")
    search_plan: Optional[SearchPlan] = Field(description="Search plan with semantic and keyword queries")

# The output for the langgraph state #
class OverseerOutput(TypedDict):
    # This is the output when the overseer is called, this populates the main State. #
    route: Literal["generic", "website_related"]
    reasoning: Optional[str]
    formatted_query: str
    search_plan: Optional[SearchPlan]