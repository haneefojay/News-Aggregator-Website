import redis.asyncio as redis
from typing import Optional
import json
from app.config import get_settings

settings = get_settings()

class CacheManager:
    _redis_client: Optional[redis.Redis] = None

    def __init__(self):
        if CacheManager._redis_client is None:
            CacheManager._redis_client = redis.from_url(
                settings.REDIS_URL, 
                decode_responses=True,
                max_connections=10
            )
        self.redis = CacheManager._redis_client
    
    async def get(self, key: str) -> Optional[dict]:
        """Get cached value"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache Get Error: {e}")
            return None
    
    async def set(self, key: str, value: dict, ttl: int = None):
        """Set cached value with TTL"""
        try:
            ttl = ttl or settings.CACHE_TTL
            await self.redis.setex(key, ttl, json.dumps(value))
            print(f"DEBUG: Cached key {key} for {ttl}s")
        except Exception as e:
            print(f"Cache Set Error: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            print(f"Cache Delete Error: {e}")

# Dependency
async def get_cache() -> CacheManager:
    return CacheManager()
