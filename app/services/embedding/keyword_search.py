from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from langchain_core.documents import Document

def build_tsquery(keyword_queries: list[list[str]]) -> str:
    or_clauses = []

    for group in keyword_queries:
        if not group:
            continue
        and_clause = " & ".join(term.replace(" ", " & ") + ":*" for term in group)
        or_clauses.append(and_clause)

    return " | ".join(or_clauses)


async def keyword_search(db: AsyncSession, keywords: list[list[str]], k: int = 5):
    ts_query = build_tsquery(keywords)
    print(f"[DEBUG] Generated tsquery: {ts_query}")

    query = text("""
            SELECT document, cmetadata
            FROM langchain_pg_embedding
            WHERE fts_vector @@ to_tsquery('english', :ts_query)
            ORDER BY ts_rank(fts_vector, to_tsquery('english', :ts_query)) DESC
            LIMIT :limit
        """)
    result = await db.execute(query, {'ts_query': ts_query, 'limit': k})
    rows = result.fetchall()
    print(f"[DEBUG] RAW ROWS: {rows}")

    print(f"[DEBUG] Keyword search - raw DB results: {result}")
    documents = [Document(page_content=row.document, metadata=row.cmetadata) for row in rows]
    print(f"[DEBUG] Keyword search - LangChain docs: {documents}")
    return documents