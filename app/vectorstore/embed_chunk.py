from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger
from app.models import Website
from app.services.embedding.service import EmbeddingService
from app.vectorstore.generate_embedding_vector import create_embedding_vector

async def embed_chunk(chunks: list[str], website: Website, db: AsyncSession):
    embedding_service = EmbeddingService(db=db, website_id=website.id)
    for index,chunk in enumerate(chunks):
        logger.info(f"Chunk: {index} - {chunk}")
        embedding_vector = await create_embedding_vector(chunk=chunk)
        metadata = {
            "length": len(chunk),
            "source_url": website.url,
            "order": index,
        }
        try:
            await embedding_service.create_embedding(chunk=chunk, embedding=embedding_vector, metadata=metadata)
        except Exception as e:
            logger.error(f"Failed to store embedding for chunk {index}: {e}")
