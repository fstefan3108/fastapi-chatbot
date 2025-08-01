from fastapi import APIRouter
from app.api.v1.endpoints import website, auth, chatbot

v1_router = APIRouter()

v1_router.include_router(website.router, prefix="/website", tags=["website"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])