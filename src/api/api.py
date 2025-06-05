from fastapi import APIRouter
from src.api.endpoints import chat_session, user, health

api_router = APIRouter()
api_router.include_router(user.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(health.router, prefix="/v1", tags=["Health"])
api_router.include_router(chat_session.router, prefix="/v1/chat-sessions", tags=["Chat Sessions"])
api_router.include_router(chat_message.router, prefix="/v1/chat-messages", tags=["Chat Messages"])




