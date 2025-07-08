from fastapi import FastAPI
from app.api.v1.api import v1_router

app = FastAPI()

@app.get("/healthy")
async def healthy():
    return {"status": "Healthy"}

app.include_router(v1_router, prefix="/v1")

