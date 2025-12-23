from fastapi import APIRouter
from app.api.v1.endpoints import articles

api_router = APIRouter()
api_router.include_router(articles.router, tags=["articles"])

@api_router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "timestamp": "now"}
