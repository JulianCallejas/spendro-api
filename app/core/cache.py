from app.core.redis_cache import RedisCache
from threading import Lock
from typing import Any, Optional

class SingletonCache:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = RedisCache()  # Usamos Redis en lugar de memoria
        return cls._instance
    
    # Mantenemos la misma interfaz que antes
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return self._cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        return self._cache.delete(key)
    
    def clear(self) -> bool:
        return self._cache.clear()
    
    def get_stats(self) -> dict:
        return self._cache.get_stats()
    
    
# for FastAPI dependency injection
def get_cache() -> SingletonCache:
    """Proveedor de dependencias para FastAPI"""
    return SingletonCache()

# Optional to use directly
cache = SingletonCache()