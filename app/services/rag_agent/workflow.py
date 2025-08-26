from typing import Optional
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.services.chat.service import ChatService
from app.services.rag_agent.agents.chatbot import Chatbot
from app.services.rag_agent.agents.overseer import Overseer
from app.services.rag_agent.agents.summarizer import Summarizer
from app.services.rag_agent.states import MainState
from app.services.rag_agent.tools.search import HybridSearchTool
from app.utils.format_chat import format_chat_history

class Workflow:
    def __init__(self, db: AsyncSession, website_id: int):
        self.workflow = self._build_workflow()
        self.hybrid_search_tool = HybridSearchTool(db=db, website_id=website_id)
        self.website_id = website_id
        self.overseer = Overseer()
        self.chatbot = Chatbot()
        self.summarizer = Summarizer()
        self.chat_service = ChatService(db=db, website_id=website_id)

    async def run(self, initial_state: MainState) -> dict:
        """Execute the complete workflow"""
        result = await self.workflow.ainvoke(initial_state)
        logger.info("[SUCCESS] Graph running...")
        return result

    def _build_workflow(self):
        builder = StateGraph(MainState)

        builder.add_node("overseer", self._overseer_node)
        builder.add_node("hybrid_search", self._hybrid_search_node)
        builder.add_node("summarizer", self._summarizer_node)
        builder.add_node("chatbot", self._chatbot_node)

        builder.add_edge(START, "overseer")
        builder.add_edge("overseer", "hybrid_search")
        builder.add_conditional_edges(
            "hybrid_search",
            self._should_summarize,
            {
                "summarizer": "summarizer",
                "chatbot": "chatbot"
            }
        )
        builder.add_edge("hybrid_search", "chatbot")
        builder.add_edge("chatbot", END)

        graph = builder.compile()
        return graph


    async def _overseer_node(self, state: MainState) -> dict:
        session_id = state.get("session_id")
        user_query = state.get("user_query", "")

        chat_history = await self.chat_service.get_chat_history(session_id=session_id)
        most_recent = chat_history[-6:] if len(chat_history) > 6 else chat_history
        formatted_history = format_chat_history(most_recent)

        result = await self.overseer.run(user_query=user_query, chat_history=formatted_history)

        logger.info(f"[SUCCESS] Overseer node executed: {
        result.get("reasoning"),
        result.get("formatted_query"),
        result.get("search_plan")
        }")

        return {
            "formatted_query": result.get("formatted_query"),
            "search_plan": result.get("search_plan"),
            "reasoning": result.get("reasoning")
        }

    async def _hybrid_search_node(self, state: MainState) -> dict:
        search_plan = state.get("search_plan", {})
        result = await self.hybrid_search_tool.hybrid_search(search_plan=search_plan)
        logger.info(f"[SUCCESS] Hybrid search node executed")

        return {"hybrid_search_results": result}

    async def _should_summarize(self, state: MainState) -> str:
        session_id = state.get("session_id")
        chat_history = await self.chat_service.get_chat_history(session_id=session_id)

        if len(chat_history) > 6:
            return "summarizer"
        else:
            return "chatbot"

    async def _summarizer_node(self, state: MainState) -> dict:
        session_id = state.get("session_id")

        chat_history = await self.chat_service.get_chat_history(session_id=session_id)
        formatted_history = format_chat_history(chat_history)

        result = await self.summarizer.run(history=formatted_history)
        logger.info(f"[SUCCESS] Summarizer node executed: \n{result}")

        return {"summary": result}

    async def _chatbot_node(self, state: MainState) -> dict:
        context = state.get("hybrid_search_results", [])
        formatted_query = state.get("formatted_query", "")
        session_id = state.get("session_id")
        summary: Optional[str] = None
        chat_history = await self.chat_service.get_chat_history(session_id=session_id)

        if len(chat_history) > 6:
            summary = state.get("summary")
            chat_history = chat_history[-3:]
        logger.info(f"[INFO] SUMMARY: {summary}")

        formatted_history = format_chat_history(chat_history)
        logger.info(f"[SUCCESS] Formatted history: \n{formatted_history}")

        result = await self.chatbot.run(
            context=context,
            user_query=formatted_query,
            history=formatted_history,
            summary=summary
        )
        logger.info(f"[SUCCESS] Chatbot node executed: \n{result}]")
        return {"final_response": result}