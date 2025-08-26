from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models.embedding import Embeddings
from app.schemas.search_plan import SearchPlan
from app.utils.rrc import reciprocal_rank_fusion
from app.vectorstore.generate_embedding_vector import create_embedding_vector
from app.crud.crud_embedding import crud_embedding
from sqlalchemy import text, func

class HybridSearchTool:
    def __init__(self, db: AsyncSession, website_id: int):
        self.db = db
        self.website_id = website_id

    async def hybrid_search(self, search_plan: SearchPlan) -> str:
        try:
            semantic_query = search_plan.rag_queries.semantic
            full_text_query = search_plan.rag_queries.keyword

            semantic_results = await self._semantic_search(semantic_query)
            logger.info(f"Semantic search results: {semantic_results}")
            full_text_results = await self._full_text_search(full_text_query)
            logger.info(f"Full text search results: {full_text_results}")

            fused_results = reciprocal_rank_fusion(semantic_results, full_text_results)
            context = "\n\n".join([e.chunk for e in fused_results])
            logger.info(f"Final context: {context}")

            return context

        except Exception as e:
            logger.error(f"[ERROR] error while creating context: {e}")
            raise e

    async def _semantic_search(self, user_prompt: str, limit: int = 5) -> list[Embeddings]:
        query_embedding = await create_embedding_vector(user_prompt)
        query_embedding_str = f"[{','.join(map(str, query_embedding))}]"
        embeddings = await crud_embedding.get_all(
            db=self.db,
            criteria=Embeddings.website_id == self.website_id,
            order=text(f"embedding <-> '{query_embedding_str}'"),
            limit=limit
        )
        return embeddings

    async def _full_text_search(self, keyword_groups: list[list[str]], limit: int = 5) -> list[Embeddings]:
        ts_query = self._build_ts_query(keyword_groups=keyword_groups)
        result = await crud_embedding.get_all(
            db=self.db,
            criteria=Embeddings.fts_vector.op('@@')(func.to_tsquery("english", ts_query)),
            order=func.ts_rank(Embeddings.fts_vector, func.to_tsquery("english", ts_query)).desc(),
            limit=limit
        )
        return result

    @staticmethod
    def _build_ts_query(keyword_groups: list[list[str]]) -> str:
        def sanitize_token(token: str) -> str:
            # Convert multi-word phrases into `<->` operator #
            words = token.split()
            return ' <-> '.join(words)

        def sanitize_group(group: list[str]) -> str:
            # OR together all tokens in this group #
            return ' | '.join(sanitize_token(token) for token in group)

        # AND together the groups #
        return ' & '.join(f"({sanitize_group(group)})" for group in keyword_groups)