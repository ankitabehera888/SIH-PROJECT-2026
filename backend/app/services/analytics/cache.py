import json
import logging
from typing import Any, Optional
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_redis_client() -> Optional[Redis]:
    """Provides a safe Redis connection with immediate timeout."""
    try:
        client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"Redis cache unavailable, falling back to database: {e}")
        return None

def get_cached_json(cache_key: str) -> Optional[Any]:
    """Safely retrieves parsed JSON data from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    try:
        val = client.get(cache_key)
        if val:
            return json.loads(val.decode("utf-8"))
    except Exception as e:
        logger.debug(f"Cache get error for key '{cache_key}': {e}")
    return None

def set_cached_json(cache_key: str, data: Any, ttl_seconds: int = 300) -> bool:
    """Safely stores serializable data in Redis cache with TTL."""
    client = get_redis_client()
    if not client:
        return False
    try:
        payload = json.dumps(data, default=str)
        client.set(cache_key, payload, ex=ttl_seconds)
        return True
    except Exception as e:
        logger.debug(f"Cache set error for key '{cache_key}': {e}")
        return False
