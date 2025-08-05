import asyncio
from app.core.logger import logger
from app.models import Website
from app.schemas.search_plan import OverseerSearchPlan
from app.services.agents.overseer import overseer_search_plan
from app.services.embedding.service import EmbeddingService
from app.utils.rrc import reciprocal_rank_fusion


class Overseer:
    def __init__(self, db, website: Website):
        self.db = db
        self.website = website
        self.embedding_service = EmbeddingService(db=db, website_url=website.url)

    async def prepare_context(self, user_prompt: str, history: list[str]) -> str:
        try:
            logger.info("[INFO] Calling overseer...")
            # Generate the search plan (semantic and keyword queries) #
            search_plan = await self._generate_search_plan(user_prompt=user_prompt, history=history)
            logger.info(f"[SUCCESS] Search plan generated: {search_plan}")

            # Run Semantic Search #
            semantic_chunks = await self.embedding_service.semantic_search(user_prompt=search_plan.rag_queries.semantic)
            logger.info(f"[SUCCESS] Semantic search performed: {semantic_chunks}")

            # Run Full Text Search #
            keyword_chunks = await self.embedding_service.full_text_search(keywords=search_plan.rag_queries.keyword)
            logger.info(f"[SUCCESS] Full text search performed: {keyword_chunks}")

            # Step 4: Fuse results
            fused_chunks = await asyncio.to_thread(
                reciprocal_rank_fusion,
                [doc.page_content for doc in semantic_chunks],
                [doc.page_content for doc in keyword_chunks]
            )
            context = "\n\n".join(fused_chunks)
            logger.info(f"[SUCCESS] Context Fusion performed, generated: {context}")

            return context
        except Exception as e:
            logger.error(f"[ERROR]: Overseer failed: {e}")
            raise e

    @staticmethod
    async def _generate_search_plan(user_prompt: str, history: list[str]) -> OverseerSearchPlan:
        if history:
            context_lines = []
            for msg in history:
                role = msg['role'].upper()
                content = msg['content']
                context_lines.append(f"{role}: {content}")

            context_str = "Previous conversation:\n" + "\n".join(context_lines) + "\n\n"
            full_prompt = f"{context_str}Current query: {user_prompt}"
        else:
            full_prompt = user_prompt

        search_plan = await overseer_search_plan.run(user_prompt=full_prompt)
        return search_plan.output