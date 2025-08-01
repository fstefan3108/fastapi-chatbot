import asyncio
from langchain_community.vectorstores import PGVector
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.core.logger import logger
from app.services.embedding.keyword_search import keyword_search
from app.utils.rrc import reciprocal_rank_fusion

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

    async def hybrid_search(self, user_prompt: str, k: int = 5):
        semantic_docs = await self._semantic_search(user_prompt=user_prompt, k=k)
        logger.info(f"[SUCCESS] Fetched embeddings / Stored Context \n Context: {semantic_docs}")
        keyword_docs = await self._full_text_search(user_prompt=user_prompt, k=k)
        logger.info(f"[SUCCESS] Fetched Keywords: {keyword_docs}")

        semantic_chunks = [doc.page_content for doc in semantic_docs]
        keyword_chunks = [doc.page_content for doc in keyword_docs]

        fused_chunks = await asyncio.to_thread(reciprocal_rank_fusion, semantic_chunks, keyword_chunks)
        logger.info(f"FULL CONTEXT: {fused_chunks}")
        full_context = "\n\n".join(fused_chunks)
        return full_context

    async def _semantic_search(self, user_prompt: str, k: int = 5):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        results = await asyncio.to_thread(retriever.get_relevant_documents, user_prompt)
        return results

    async def _full_text_search(self, user_prompt: str, k: int = 5):
        results = await keyword_search(db=self.db, user_prompt=user_prompt, k=k)
        return results
