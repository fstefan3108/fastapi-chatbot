from typing import Optional

from pydantic import BaseModel

class EmbeddingCreate(BaseModel):
    website_id: int
    chunk: str
    embedding: list[float]
    chunk_metadata: Optional[dict] = None