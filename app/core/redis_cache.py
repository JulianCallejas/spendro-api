import json
import os
from typing import Optional, Any
import redis
from redis.exceptions import RedisError
from dotenv import load_dotenv
from datetime import timedelta

from app.core.config import settings

load_dotenv()

class RedisCache:
    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=False  # Manually decode responses for more control
        )
        self._default_ttl = settings.CACHE_TTL_MINUTES * 60

    def get(self, key: str) -> Optional[Any]:
        """Retrieves a value from Redis"""
        try:
            serialized_data = self._redis.get(key)
            if serialized_data is None:
                return None
            return json.loads(serialized_data)
        except (RedisError, json.JSONDecodeError) as e:
            print(f"Error getting cache key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Saves a value to Redis"""
        try:
            serialized_value = json.dumps(value)
            actual_ttl = ttl if ttl is not None else self._default_ttl
            return self._redis.setex(key, timedelta(seconds=actual_ttl), serialized_value)
        except (RedisError, TypeError) as e:
            print(f"Error setting cache key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Removes a value from Redis"""
        try:
            return self._redis.delete(key) > 0
        except RedisError as e:
            print(f"Error deleting cache key {key}: {str(e)}")
            return False

    def clear(self) -> bool:
        """Clears the entire Redis cache"""
        try:
            self._redis.flushdb()
            return True
        except RedisError as e:
            print(f"Error clearing cache: {str(e)}")
            return False

    def get_stats(self) -> dict:
        """Retrieves cache statistics"""
        try:
            return {
                'connected_clients': self._redis.info().get('connected_clients', 0),
                'used_memory': self._redis.info().get('used_memory', 0),
                'keys_count': self._redis.dbsize()
            }
        except RedisError as e:
            print(f"Error getting cache stats: {str(e)}")
            return {}