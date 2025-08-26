from typing import Optional
from app.crud.crud_embedding import crud_embedding
from app.models.embedding import Embeddings
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.embedding import EmbeddingCreate
from app.utils.db_transaction import db_transactional_async
from app.core.logger import logger

class EmbeddingService:
    def __init__(self, db: AsyncSession, website_id: int):
        self.db = db
        self.website_id = website_id

    @db_transactional_async
    async def create_embedding(self, chunk: str, embedding: list[float], metadata: Optional[dict] = None) -> Embeddings:
        try:
            embedding_create = EmbeddingCreate(
                website_id=self.website_id,
                chunk=chunk,
                embedding=embedding,
                chunk_metadata=metadata
            )
            new_embedding = await crud_embedding.create(db=self.db, data=embedding_create.model_dump())
            logger.info("[SUCCESS] Embeddings created and stored succesfully.")
            return new_embedding
        except Exception as e:
            logger.error(f"[ERROR] Error creating embedding: {e}")
            raise e