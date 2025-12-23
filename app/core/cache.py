import redis.asyncio as redis
from typing import Optional
import json
from app.config import get_settings

settings = get_settings()

class CacheManager:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def get(self, key: str) -> Optional[dict]:
        """Get cached value"""
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = None):
        """Set cached value with TTL"""
        ttl = ttl or settings.CACHE_TTL
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete cached value"""
        await self.redis.delete(key)

# Dependency
async def get_cache() -> CacheManager:
    return CacheManager()
