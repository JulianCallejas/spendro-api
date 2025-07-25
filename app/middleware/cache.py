from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json
import time
from typing import Dict, Any, Optional
import sys

from app.core.config import settings

class CacheMiddleware(BaseHTTPMiddleware):
    """In-memory caching middleware for user metadata"""
    
    def __init__(self, app):
        super().__init__(app)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {"hits": 0, "misses": 0, "size_mb": 0}
    
    async def dispatch(self, request: Request, call_next):
        # Add cache utilities to request
        request.state.cache = self
        
        response = await call_next(request)
        return response
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache"""
        if key not in self.cache:
            self.cache_stats["misses"] += 1
            return None
        
        item = self.cache[key]
        current_time = time.time()
        
        # Check if expired (TTL in minutes)
        if current_time - item["timestamp"] > (settings.CACHE_TTL_MINUTES * 60):
            del self.cache[key]
            self.cache_stats["misses"] += 1
            return None
        
        # Update last accessed time
        item["last_accessed"] = current_time
        self.cache_stats["hits"] += 1
        return item["data"]
    
    def set(self, key: str, data: Dict[str, Any]) -> bool:
        """Set item in cache"""
        current_time = time.time()
        
        # Check cache size limit
        if self._get_cache_size_mb() >= settings.CACHE_MAX_SIZE_MB:
            self._evict_oldest()
        
        self.cache[key] = {
            "data": data,
            "timestamp": current_time,
            "last_accessed": current_time
        }
        
        self._update_cache_size()
        return True
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        if key in self.cache:
            del self.cache[key]
            self._update_cache_size()
            return True
        return False
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.cache_stats = {"hits": 0, "misses": 0, "size_mb": 0}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate_percent": round(hit_rate, 2),
            "size_mb": self.cache_stats["size_mb"],
            "items_count": len(self.cache)
        }
    
    def _get_cache_size_mb(self) -> float:
        """Calculate current cache size in MB"""
        total_size = sys.getsizeof(self.cache)
        for item in self.cache.values():
            total_size += sys.getsizeof(item)
            total_size += sys.getsizeof(item["data"])
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _update_cache_size(self):
        """Update cache size statistics"""
        self.cache_stats["size_mb"] = round(self._get_cache_size_mb(), 2)
    
    def _evict_oldest(self):
        """Evict least recently used items"""
        if not self.cache:
            return
        
        # Sort by last accessed time and remove oldest 25%
        sorted_items = sorted(
            self.cache.items(),
            key=lambda x: x[1]["last_accessed"]
        )
        
        items_to_remove = max(1, len(sorted_items) // 4)
        for i in range(items_to_remove):
            key = sorted_items[i][0]
            if key in self.cache:
                del self.cache[key]
        
        self._update_cache_size()