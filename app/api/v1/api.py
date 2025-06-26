from fastapi import APIRouter
from app.api.v1.endpoints import website, auth, chatbot

v1_router = APIRouter()

v1_router.include_router(website.router, tags=["website"], prefix="/website")
v1_router.include_router(auth.router, tags=["auth"], prefix="/auth")
v1_router.include_router(chatbot.router, tags=["chatbot"], prefix="/chatbot")