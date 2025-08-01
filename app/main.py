from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.api import v1_router
from app.vectorstore.sentence_transformer import get_sentence_transformer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔁 Preload model at startup
    get_sentence_transformer()
    print("✅ SentenceTransformer preloaded.")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/healthy")
async def healthy():
    return {"status": "Healthy"}

app.include_router(v1_router, prefix="/v1")
