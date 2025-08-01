from sqlalchemy import text
from langchain.schema import Document
from sqlalchemy.ext.asyncio import AsyncSession

async def keyword_search(db: AsyncSession, user_prompt: str, k: int = 5):
    query = text("""
            SELECT document, cmetadata
            FROM langchain_pg_embedding
            WHERE fts_vector @@ plainto_tsquery('english', :query)
            ORDER BY ts_rank(fts_vector, plainto_tsquery('english', :query)) DESC
            LIMIT :limit
        """)
    result = await db.execute(query, {'query': user_prompt, 'limit': k})
    rows = result.fetchall()
    print(f"[DEBUG] RAW ROWS: {rows}")

    print(f"[DEBUG] Keyword search - raw DB results: {result}")
    documents = [Document(page_content=row.document, metadata=row.cmetadata) for row in rows]
    print(f"[DEBUG] Keyword search - LangChain docs: {documents}")
    return documents