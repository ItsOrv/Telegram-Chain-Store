import redis
from .settings import get_settings
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    _instance = None

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            try:
                logger.debug(f"Connecting to Redis at {self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}")
                self._client = redis.Redis(
                    host=self.settings.REDIS_HOST,
                    port=self.settings.REDIS_PORT,
                    db=self.settings.REDIS_DB,
                    password=self.settings.REDIS_PASSWORD,
                    ssl=self.settings.REDIS_SSL,
                    socket_timeout=self.settings.REDIS_SOCKET_TIMEOUT,
                    decode_responses=True
                )
                # Test connection
                self._client.ping()
                logger.info("Redis connection established successfully")
            except redis.ConnectionError as e:
                logger.error(f"Could not connect to Redis: {e}")
                logger.debug(f"Redis connection details: {self.settings.REDIS_HOST}:{self.settings.REDIS_PORT}")
                self._client = None
                raise
            except Exception as e:
                logger.error(f"Unexpected Redis error: {str(e)}")
                self._client = None
                raise
        return self._client

    def get_connection(self) -> redis.Redis:
        """Get Redis connection"""
        return self.client

    # User State Management
    def set_user_state(self, user_id: int, state: str, ttl: int = 3600):
        """Set user state with TTL"""
        key = f"user_state:{user_id}"
        self.client.set(key, state, ex=ttl)

    def get_user_state(self, user_id: int) -> str:
        """Get user current state"""
        key = f"user_state:{user_id}"
        return self.client.get(key)

    # Rate Limiting
    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """
        Check if rate limit is exceeded
        :param key: Rate limit key (e.g. user_id:action)
        :param limit: Maximum number of requests
        :param window: Time window in seconds
        """
        current = self.client.incr(key)
        if current == 1:
            self.client.expire(key, window)
        return current <= limit

    # Cache Management
    def cache_set(self, key: str, value: str, ttl: int = 300):
        """Set cache with TTL"""
        self.client.set(key, value, ex=ttl)

    def cache_get(self, key: str) -> str:
        """Get cached value"""
        return self.client.get(key)

    # Distributed Lock
    def acquire_lock(self, lock_name: str, ttl: int = 30) -> bool:
        """Acquire distributed lock"""
        return bool(self.client.set(f"lock:{lock_name}", "1", nx=True, ex=ttl))

    def release_lock(self, lock_name: str):
        """Release distributed lock"""
        self.client.delete(f"lock:{lock_name}")

# Create global instance
redis_config = RedisManager()

# Export the instance for other modules
__all__ = ['redis_config']
