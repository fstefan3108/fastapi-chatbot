from typing import Optional
from sqlalchemy import text, func
from app.crud.crud_embedding import crud_embedding
from app.models.embedding import Embeddings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.embedding import EmbeddingCreate
from app.utils.rrc import reciprocal_rank_fusion
from app.vectorstore.generate_embedding_vector import create_embedding_vector
from app.utils.db_transaction import db_transactional_async

class EmbeddingService:
    def __init__(self, db: AsyncSession, website_id: int):
        self.db = db
        self.website_id = website_id

    @db_transactional_async
    async def create_embedding(self, chunk: str, embedding: list[float], metadata: Optional[dict] = None) -> Embeddings:
        embedding_create = EmbeddingCreate(
            website_id=self.website_id,
            chunk=chunk,
            embedding=embedding,
            chunk_metadata=metadata
        )
        new_embedding = await crud_embedding.create(db=self.db, data=embedding_create.model_dump())
        return new_embedding

    async def hybrid_search(self, user_prompt: str, limit: int = 5):
        semantic_results = self._semantic_search(user_prompt, limit)
        full_text_results = self._keyword_search(user_prompt, limit)

        fused_results = reciprocal_rank_fusion(semantic_results, full_text_results)
        context = "\n\n".join(fused_results)
        return context

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

    async def _keyword_search(self, user_prompt: str, limit: int = 5) -> list[Embeddings]:
        result = await crud_embedding.get_all(
            db=self.db,
            criteria=Embeddings.fts_vector.match(user_prompt),
            order=func.ts_rank(Embeddings.fts_vector, func.plainto_tsquery("english", user_prompt)).desc(),
            limit=limit
        )
        return result