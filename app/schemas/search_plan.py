from pydantic import BaseModel, Field

class RagQueries(BaseModel):
    semantic: str = Field(description="Semantic search query for embeddings")
    keyword: list[list[str]] = Field(
        description="Keyword search queries for full-text search, structured as a list of keyword lists"
    )

class OverseerSearchPlan(BaseModel):
    rag_queries: RagQueries = Field(description="Queries to use for semantic and keyword searches")
