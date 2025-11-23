"""
Cache implementations with Redis and in-memory fallback.
"""

import json
import pickle
from typing import Optional, Any, Dict
from datetime import datetime
import hashlib

from core.interfaces import ICache, ILogger
from core.exceptions import CacheConnectionError, CacheOperationError


class InMemoryCache(ICache):
    """
    Simple in-memory cache implementation.
    
    Useful for development and testing.
    """
    
    def __init__(self, logger: ILogger, max_size: int = 1000):
        """
        Initialize in-memory cache.
        
        Args:
            logger: Logger instance
            max_size: Maximum number of items to cache
        """
        self.logger = logger
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order = []

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        if key not in self._cache:
            self.logger.debug(f"Cache miss for key: {key}")
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if entry["expires_at"] and datetime.now() > entry["expires_at"]:
            self.logger.debug(f"Cache expired for key: {key}")
            await self.delete(key)
            return None
        
        # Update access order for LRU
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        self.logger.debug(f"Cache hit for key: {key}")
        return entry["value"]

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Store value in cache."""
        try:
            # Calculate expiration
            expires_at = None
            if ttl:
                from datetime import timedelta
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Evict oldest item if cache is full
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
                self.logger.debug(f"Evicted cache key: {oldest_key}")
            
            # Store value
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.now()
            }
            
            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            self.logger.debug(f"Cache set for key: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting cache for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            self.logger.debug(f"Cache deleted for key: {key}")
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache

    async def clear(self) -> bool:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
        self.logger.info("Cache cleared")
        return True

    async def health_check(self) -> bool:
        """Check if cache is responding."""
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "utilization": len(self._cache) / self.max_size * 100
        }


class RedisCache(ICache):
    """
    Redis-based cache implementation.
    
    Provides distributed caching with TTL support.
    """
    
    def __init__(
        self,
        redis_client,
        logger: ILogger,
        default_ttl: int = 3600,
        key_prefix: str = "researchapi"
    ):
        """
        Initialize Redis cache.
        
        Args:
            redis_client: Redis client instance
            logger: Logger instance
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis = redis_client
        self.logger = logger
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.key_prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis cache."""
        try:
            redis_key = self._make_key(key)
            data = await self.redis.get(redis_key)
            
            if data is None:
                self.logger.debug(f"Cache miss for key: {key}")
                return None
            
            # Deserialize
            value = pickle.loads(data)
            self.logger.debug(f"Cache hit for key: {key}")
            return value
            
        except Exception as e:
            self.logger.error(f"Error getting cache for key {key}: {e}")
            raise CacheOperationError(f"Failed to get cache: {str(e)}") from e

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Store value in Redis cache."""
        try:
            redis_key = self._make_key(key)
            
            # Serialize value
            data = pickle.dumps(value)
            
            # Set with TTL
            ttl_seconds = ttl or self.default_ttl
            await self.redis.setex(redis_key, ttl_seconds, data)
            
            self.logger.debug(f"Cache set for key: {key} (TTL: {ttl_seconds}s)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting cache for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            redis_key = self._make_key(key)
            result = await self.redis.delete(redis_key)
            
            if result > 0:
                self.logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting cache for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            redis_key = self._make_key(key)
            result = await self.redis.exists(redis_key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Error checking cache existence for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries with our prefix."""
        try:
            # Find all keys with our prefix
            pattern = f"{self.key_prefix}:*"
            keys = await self.redis.keys(pattern)
            
            if keys:
                await self.redis.delete(*keys)
                self.logger.info(f"Cleared {len(keys)} cache entries")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

    async def health_check(self) -> bool:
        """Check if Redis is responding."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            info = await self.redis.info("stats")
            return {
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "used_memory": info.get("used_memory_human", "unknown")
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        MD5 hash of the arguments
    """
    # Create a string representation of all arguments
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    key_string = "|".join(key_parts)
    
    # Generate MD5 hash
    return hashlib.md5(key_string.encode()).hexdigest()


class CacheManager:
    """
    Cache manager that handles Redis with in-memory fallback.
    """
    
    def __init__(
        self,
        redis_cache: Optional[RedisCache],
        memory_cache: InMemoryCache,
        logger: ILogger
    ):
        """
        Initialize cache manager.
        
        Args:
            redis_cache: Redis cache instance (optional)
            memory_cache: In-memory cache instance (fallback)
            logger: Logger instance
        """
        self.redis_cache = redis_cache
        self.memory_cache = memory_cache
        self.logger = logger
        self._redis_available = redis_cache is not None

    async def get(self, key: str) -> Optional[Any]:
        """Get from Redis, fallback to memory."""
        if self._redis_available and self.redis_cache:
            try:
                return await self.redis_cache.get(key)
            except Exception as e:
                self.logger.warning(f"Redis get failed, using memory cache: {e}")
                self._redis_available = False
        
        return await self.memory_cache.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set in both Redis and memory."""
        success = True
        
        if self._redis_available and self.redis_cache:
            try:
                success = await self.redis_cache.set(key, value, ttl)
            except Exception as e:
                self.logger.warning(f"Redis set failed: {e}")
                self._redis_available = False
                success = False
        
        # Always set in memory as fallback
        memory_success = await self.memory_cache.set(key, value, ttl)
        
        return success or memory_success

    async def delete(self, key: str) -> bool:
        """Delete from both caches."""
        results = []
        
        if self._redis_available and self.redis_cache:
            try:
                results.append(await self.redis_cache.delete(key))
            except Exception:
                pass
        
        results.append(await self.memory_cache.delete(key))
        return any(results)

    async def clear(self) -> bool:
        """Clear both caches."""
        results = []
        
        if self._redis_available and self.redis_cache:
            try:
                results.append(await self.redis_cache.clear())
            except Exception:
                pass
        
        results.append(await self.memory_cache.clear())
        return any(results)

    async def health_check(self) -> Dict[str, bool]:
        """Check health of both caches."""
        redis_healthy = False
        
        if self.redis_cache:
            redis_healthy = await self.redis_cache.health_check()
            self._redis_available = redis_healthy
        
        memory_healthy = await self.memory_cache.health_check()
        
        return {
            "redis": redis_healthy,
            "memory": memory_healthy
        }
