"""
Base adapter implementation with common functionality.
"""

from abc import abstractmethod
from typing import Optional
import asyncio

from core.interfaces import IArticleAdapter, IHTTPClient
from core.entities import Article, SearchQuery, SearchResult, SourceType
from core.exceptions import AdapterException
import logging 

class BaseAdapter(IArticleAdapter):
    """
    Base implementation for all article adapters.
    
    Provides common functionality like rate limiting, logging, and error handling.
    """
    
    def __init__(
        self,
        http_client: IHTTPClient,
        logger: logging.Logger,
        source_type: SourceType,
        base_url: str,
        api_key: Optional[str] = None,
        delay_between_requests: float = 0
    ):
        """
        Initialize base adapter.
        
        Args:
            http_client: HTTP client instance
            logger: Logger instance
            source_type: Type of source (arXiv, IEEE, etc.)
            base_url: Base URL for the API
            api_key: API key if required
            delay_between_requests: Delay in seconds between requests
        """
        self._http_client = http_client
        self._logger = logger
        self._source_type = source_type
        self._base_url = base_url
        self._api_key = api_key
        self._delay = delay_between_requests
        self._last_request_time = 0.0

    @property
    def source_type(self) -> SourceType:
        """Return the source type this adapter handles."""
        return self._source_type

    @property
    def is_available(self) -> bool:
        """Check if the adapter is properly configured."""
        # Override this if API key is required
        return True

    @property
    def get_logger(self) -> logging.Logger:
        """Get logger instance."""
        return self._logger

    @property
    def http_client(self) -> IHTTPClient:
        """Get HTTP client instance."""
        return self._http_client

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting delay if configured."""
        if self._delay > 0:
            import time
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            
            if time_since_last < self._delay:
                wait_time = self._delay - time_since_last
                self._logger.debug(
                    f"Rate limiting: waiting {wait_time:.2f}s",
                    source=self._source_type.value
                )
                await asyncio.sleep(wait_time)
            
            self._last_request_time = time.time()

    @abstractmethod
    async def search(self, query: SearchQuery) -> SearchResult:
        """
        Search for articles - must be implemented by subclasses.
        
        Args:
            query: SearchQuery object containing search parameters
            
        Returns:
            SearchResult containing articles and metadata
        """
        pass

    @abstractmethod
    async def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve a single article - must be implemented by subclasses.
        
        Args:
            article_id: Unique identifier for the article
            
        Returns:
            Article if found, None otherwise
        """
        pass

    async def health_check(self) -> bool:
        """
        Check if the external API is responding.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Try a simple request to check connectivity
            # Override this method for API-specific health checks
            return True
        except Exception as e:
            self._logger.error(
                f"Health check failed for {self._source_type.value}",
                error=str(e)
            )
            return False

    def _build_url(self, endpoint: str = "") -> str:
        """
        Build full URL from base URL and endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL
        """
        if endpoint:
            return f"{self._base_url}/{endpoint}".replace("//", "/").replace(":/", "://")
        return self._base_url

    def _add_api_key(self, params: dict) -> dict:
        """
        Add API key to parameters if configured.
        
        Args:
            params: Request parameters
            
        Returns:
            Parameters with API key added
        """
        if self._api_key:
            params = params.copy()
            params["api_key"] = self._api_key
        return params

    async def _handle_adapter_error(self, error: Exception, context: str) -> None:
        """
        Handle adapter errors with logging.
        
        Args:
            error: Exception that occurred
            context: Context information
        """
        self._logger.error(
            f"Adapter error in {context}",
            source=self._source_type.value,
            error=str(error),
            error_type=type(error).__name__
        )
        
        # Re-raise as AdapterException if not already
        if not isinstance(error, AdapterException):
            raise AdapterException(
                f"Error in {self._source_type.value} adapter: {str(error)}"
            ) from error
        raise
