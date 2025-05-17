from fastapi import APIRouter
from app.api.v1.endpoints import meta_webhook, chat

api_router_v1 = APIRouter()
api_router_v1.include_router(meta_webhook.router, prefix="/meta", tags=["Meta Webhook"])
api_router_v1.include_router(chat.router, prefix="/chat", tags=["Direct Chat (Test)"])