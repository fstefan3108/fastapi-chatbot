import asyncio
from langchain_community.vectorstores import PGVector
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.core.logger import logger
from app.services.embedding.keyword_search import keyword_search

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

class EmbeddingService:
    def __init__(self, db: AsyncSession, website_url: str):
        self.db = db
        self.website_url = website_url
        self.vectorstore = PGVector(
            connection_string=settings.database_url_sync,
            embedding_function=embedding_model,
            collection_name="embeddings",
        )

    async def create_embeddings(self, chunks: list[str]) -> None:
        metadatas = [{
            "source_url": self.website_url,
            "order": i,
            "length": len(chunk)
        } for i, chunk in enumerate(chunks)]

        await asyncio.to_thread(
            self.vectorstore.add_texts,
            texts=chunks,
            metadatas=metadatas
        )
        logger.info("[SUCCESS] Embeddings created successfully.")

    async def semantic_search(self, user_prompt: str, k: int = 5):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        results = await asyncio.to_thread(retriever.get_relevant_documents, user_prompt)
        return results

    async def full_text_search(self, keywords: list[list[str]], k: int = 5):
        results = await keyword_search(db=self.db, keywords=keywords, k=k)
        return results
