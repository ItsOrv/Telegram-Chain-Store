from typing import Any, Optional
import redis
from src.config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set cache value with expiry"""
        try:
            self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def delete(self, key: str):
        """Delete cached value"""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

cache_manager = CacheManager()
