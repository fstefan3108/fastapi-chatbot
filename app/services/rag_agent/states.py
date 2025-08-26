from typing import TypedDict, NotRequired, Any
from app.schemas.search_plan import SearchPlan
from sqlalchemy.dialects.postgresql import UUID

class MainState(TypedDict):
    # Original input
    user_query: str
    session_id: UUID

    # Overseer decisions and output #
    formatted_query: NotRequired[str]
    reasoning: NotRequired[str]
    search_plan: NotRequired[SearchPlan]  # Only populated if route is hybrid_search

    # Summarizer Summary #
    summary: NotRequired[str]

    # search results #
    hybrid_search_results: NotRequired[Any]

    # Final chatbot response #
    final_response: NotRequired[str]

