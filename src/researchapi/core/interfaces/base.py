"""
Abstract interfaces for the domain layer.

These define contracts that infrastructure implementations must follow.
Framework-independent and part of the core domain.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from researchapi.core.entities import Article, SearchQuery, SearchResult, SourceType


class IArticleAdapter(ABC):
    """
    Abstract interface for article source adapters.
    
    All external API adapters must implement this interface.
    """
    
    @property
    @abstractmethod
    def source_type(self) -> SourceType:
        """Return the source type this adapter handles."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is properly configured and available."""
        pass

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResult:
        """
        Search for articles using the provided query.
        
        Args:
            query: SearchQuery object containing search parameters
            
        Returns:
            SearchResult containing articles and metadata
            
        Raises:
            AdapterException: If search fails
        """
        pass

    @abstractmethod
    async def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve a single article by its ID.
        
        Args:
            article_id: Unique identifier for the article
            
        Returns:
            Article if found, None otherwise
            
        Raises:
            AdapterException: If retrieval fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the external API is responding.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class ICache(ABC):
    """Abstract interface for cache implementations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists, None otherwise
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if cache is responding.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class IRateLimiter(ABC):
    """Abstract interface for rate limiting."""
    
    @abstractmethod
    async def acquire(self, identifier: str) -> bool:
        """
        Attempt to acquire a rate limit token.
        
        Args:
            identifier: Unique identifier for rate limiting
            
        Returns:
            True if allowed, False if rate limited
        """
        pass

    @abstractmethod
    async def reset(self, identifier: str) -> None:
        """
        Reset rate limit for an identifier.
        
        Args:
            identifier: Unique identifier
        """
        pass

    @abstractmethod
    async def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests for an identifier.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        pass


class ILogger(Protocol):
    """Protocol for logger implementations."""
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        ...

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        ...

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        ...

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        ...

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        ...


class IHTTPClient(ABC):
    """Abstract interface for HTTP client implementations."""
    
    @abstractmethod
    async def get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None
    ) -> dict:
        """
        Perform GET request.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
            
        Raises:
            AdapterConnectionError: If connection fails
            AdapterTimeoutError: If request times out
        """
        pass

    @abstractmethod
    async def post(
        self,
        url: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None
    ) -> dict:
        """
        Perform POST request.
        
        Args:
            url: Target URL
            data: Form data
            json: JSON data
            headers: Request headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        pass


class IResponseParser(ABC):
    """Abstract interface for response parsers."""
    
    @abstractmethod
    def parse(self, raw_data: any) -> List[Article]:
        """
        Parse raw API response into Article entities.
        
        Args:
            raw_data: Raw response from external API
            
        Returns:
            List of Article entities
            
        Raises:
            AdapterParsingError: If parsing fails
        """
        pass

    @abstractmethod
    def validate(self, raw_data: any) -> bool:
        """
        Validate raw response structure.
        
        Args:
            raw_data: Raw response from external API
            
        Returns:
            True if valid, False otherwise
        """
        pass
