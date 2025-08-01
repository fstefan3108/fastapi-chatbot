import asyncio
from app.vectorstore.sentence_transformer import get_sentence_transformer
import numpy as np

def normalize(v: list[float]) -> list[float]:
    norm = np.linalg.norm(v)
    return (np.array(v) / norm).tolist() if norm != 0 else v

async def create_embedding_vector(chunk: str) -> list[float]:
    model = get_sentence_transformer()
    embedding = await asyncio.to_thread(model.encode, chunk)
    return normalize(embedding.tolist())
