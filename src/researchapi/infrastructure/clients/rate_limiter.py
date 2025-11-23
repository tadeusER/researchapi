"""
Rate limiter implementation using sliding window algorithm.
"""

import time
from typing import Dict, Optional
from collections import deque
import asyncio

from core.interfaces import IRateLimiter, ILogger


class InMemoryRateLimiter(IRateLimiter):
    """
    In-memory rate limiter using sliding window algorithm.
    
    Thread-safe and async-compatible.
    """
    
    def __init__(
        self,
        logger: ILogger,
        default_requests: int = 60,
        default_period: int = 60
    ):
        """
        Initialize rate limiter.
        
        Args:
            logger: Logger instance
            default_requests: Default number of requests allowed
            default_period: Default time period in seconds
        """
        self.logger = logger
        self.default_requests = default_requests
        self.default_period = default_period
        
        # Store request timestamps per identifier
        self._windows: Dict[str, deque] = {}
        
        # Store custom limits per identifier
        self._limits: Dict[str, tuple] = {}
        
        # Lock for thread safety
        self._lock = asyncio.Lock()

    def set_limit(
        self,
        identifier: str,
        requests: int,
        period: int
    ) -> None:
        """
        Set custom rate limit for an identifier.
        
        Args:
            identifier: Unique identifier
            requests: Number of requests allowed
            period: Time period in seconds
        """
        self._limits[identifier] = (requests, period)
        self.logger.debug(
            f"Rate limit set for {identifier}",
            requests=requests,
            period=period
        )

    async def acquire(self, identifier: str) -> bool:
        """
        Attempt to acquire a rate limit token.
        
        Args:
            identifier: Unique identifier for rate limiting
            
        Returns:
            True if allowed, False if rate limited
        """
        async with self._lock:
            current_time = time.time()
            
            # Get or create window for this identifier
            if identifier not in self._windows:
                self._windows[identifier] = deque()
            
            window = self._windows[identifier]
            
            # Get limits for this identifier
            requests, period = self._limits.get(
                identifier,
                (self.default_requests, self.default_period)
            )
            
            # Remove expired timestamps
            cutoff_time = current_time - period
            while window and window[0] < cutoff_time:
                window.popleft()
            
            # Check if we can proceed
            if len(window) < requests:
                window.append(current_time)
                remaining = requests - len(window)
                
                self.logger.debug(
                    f"Rate limit acquired for {identifier}",
                    remaining=remaining,
                    total=requests
                )
                return True
            else:
                # Calculate when the next slot will be available
                oldest_timestamp = window[0]
                retry_after = int(oldest_timestamp + period - current_time) + 1
                
                self.logger.warning(
                    f"Rate limit exceeded for {identifier}",
                    retry_after=retry_after
                )
                return False

    async def reset(self, identifier: str) -> None:
        """
        Reset rate limit for an identifier.
        
        Args:
            identifier: Unique identifier
        """
        async with self._lock:
            if identifier in self._windows:
                self._windows[identifier].clear()
                self.logger.info(f"Rate limit reset for {identifier}")

    async def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests for an identifier.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        async with self._lock:
            if identifier not in self._windows:
                requests, _ = self._limits.get(
                    identifier,
                    (self.default_requests, self.default_period)
                )
                return requests
            
            current_time = time.time()
            window = self._windows[identifier]
            requests, period = self._limits.get(
                identifier,
                (self.default_requests, self.default_period)
            )
            
            # Remove expired timestamps
            cutoff_time = current_time - period
            while window and window[0] < cutoff_time:
                window.popleft()
            
            return max(0, requests - len(window))

    async def cleanup_old_windows(self) -> None:
        """Remove old windows to prevent memory leaks."""
        async with self._lock:
            current_time = time.time()
            identifiers_to_remove = []
            
            for identifier, window in self._windows.items():
                _, period = self._limits.get(
                    identifier,
                    (self.default_requests, self.default_period)
                )
                cutoff_time = current_time - (period * 2)
                
                # Remove expired timestamps
                while window and window[0] < cutoff_time:
                    window.popleft()
                
                # If window is empty, mark for removal
                if not window:
                    identifiers_to_remove.append(identifier)
            
            # Remove empty windows
            for identifier in identifiers_to_remove:
                del self._windows[identifier]
            
            if identifiers_to_remove:
                self.logger.debug(
                    f"Cleaned up {len(identifiers_to_remove)} rate limit windows"
                )


class RedisRateLimiter(IRateLimiter):
    """
    Redis-based rate limiter for distributed systems.
    
    Uses Redis sorted sets for efficient sliding window implementation.
    """
    
    def __init__(
        self,
        redis_client,
        logger: ILogger,
        default_requests: int = 60,
        default_period: int = 60
    ):
        """
        Initialize Redis rate limiter.
        
        Args:
            redis_client: Redis client instance
            logger: Logger instance
            default_requests: Default number of requests allowed
            default_period: Default time period in seconds
        """
        self.redis = redis_client
        self.logger = logger
        self.default_requests = default_requests
        self.default_period = default_period
        self._limits: Dict[str, tuple] = {}

    def set_limit(
        self,
        identifier: str,
        requests: int,
        period: int
    ) -> None:
        """Set custom rate limit for an identifier."""
        self._limits[identifier] = (requests, period)

    async def acquire(self, identifier: str) -> bool:
        """
        Attempt to acquire a rate limit token using Redis.
        
        Uses Redis sorted sets with timestamps as scores.
        """
        current_time = time.time()
        key = f"rate_limit:{identifier}"
        
        # Get limits
        requests, period = self._limits.get(
            identifier,
            (self.default_requests, self.default_period)
        )
        
        # Remove old entries
        cutoff_time = current_time - period
        await self.redis.zremrangebyscore(key, 0, cutoff_time)
        
        # Count current requests
        count = await self.redis.zcard(key)
        
        if count < requests:
            # Add current timestamp
            await self.redis.zadd(key, {str(current_time): current_time})
            # Set expiration
            await self.redis.expire(key, period * 2)
            return True
        
        return False

    async def reset(self, identifier: str) -> None:
        """Reset rate limit for an identifier."""
        key = f"rate_limit:{identifier}"
        await self.redis.delete(key)
        self.logger.info(f"Rate limit reset for {identifier}")

    async def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for an identifier."""
        current_time = time.time()
        key = f"rate_limit:{identifier}"
        
        requests, period = self._limits.get(
            identifier,
            (self.default_requests, self.default_period)
        )
        
        # Remove old entries
        cutoff_time = current_time - period
        await self.redis.zremrangebyscore(key, 0, cutoff_time)
        
        # Count current requests
        count = await self.redis.zcard(key)
        
        return max(0, requests - count)
