"""
Robust HTTP client with retry logic, rate limiting, and error handling.
"""

import asyncio
import time
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from core.exceptions import (
    AdapterConnectionError,
    AdapterTimeoutError,
    AdapterRateLimitError,
    AdapterResponseError
)
from core.interfaces import IHTTPClient, ILogger
from infrastructure.config.settings import HTTPClientSettings


class HTTPClient(IHTTPClient):
    """
    HTTP client with automatic retries, rate limiting, and error handling.
    """
    
    def __init__(
        self,
        settings: HTTPClientSettings,
        logger: ILogger,
        rate_limiter: Optional[Any] = None
    ):
        self.settings = settings
        self.logger = logger
        self.rate_limiter = rate_limiter
        
        # Create httpx client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.http_timeout),
            limits=httpx.Limits(
                max_connections=settings.http_connection_pool_size,
                max_keepalive_connections=settings.http_max_keepalive_connections
            ),
            follow_redirects=True
        )

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Perform GET request with retry logic.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Request headers
            timeout: Request timeout (overrides default)
            retry_enabled: Enable retry logic
            
        Returns:
            Response data as dictionary
            
        Raises:
            AdapterConnectionError: Connection failed
            AdapterTimeoutError: Request timed out
            AdapterRateLimitError: Rate limit exceeded
            AdapterResponseError: Invalid response
        """
        # Apply rate limiting if available
        if self.rate_limiter:
            await self._wait_for_rate_limit(url)
        
        # Set default headers
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        # Use custom timeout if provided
        request_timeout = timeout or self.settings.http_timeout
        
        try:
            if retry_enabled:
                response = await self._get_with_retry(
                    url=url,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout
                )
            else:
                response = await self.client.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=request_timeout
                )
            
            return await self._process_response(response)
            
        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout for URL: {url}", error=str(e))
            raise AdapterTimeoutError(f"Request timed out: {url}") from e
            
        except httpx.NetworkError as e:
            self.logger.error(f"Network error for URL: {url}", error=str(e))
            raise AdapterConnectionError(f"Network error: {url}") from e
            
        except Exception as e:
            self.logger.error(f"Unexpected error for URL: {url}", error=str(e))
            raise AdapterConnectionError(f"Request failed: {str(e)}") from e

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Perform POST request with retry logic.
        
        Args:
            url: Target URL
            data: Form data
            json: JSON data
            headers: Request headers
            timeout: Request timeout
            retry_enabled: Enable retry logic
            
        Returns:
            Response data as dictionary
        """
        if self.rate_limiter:
            await self._wait_for_rate_limit(url)
        
        request_headers = self._get_default_headers()
        if headers:
            request_headers.update(headers)
        
        request_timeout = timeout or self.settings.http_timeout
        
        try:
            if retry_enabled:
                response = await self._post_with_retry(
                    url=url,
                    data=data,
                    json=json,
                    headers=request_headers,
                    timeout=request_timeout
                )
            else:
                response = await self.client.post(
                    url,
                    data=data,
                    json=json,
                    headers=request_headers,
                    timeout=request_timeout
                )
            
            return await self._process_response(response)
            
        except httpx.TimeoutException as e:
            self.logger.error(f"Request timeout for URL: {url}", error=str(e))
            raise AdapterTimeoutError(f"Request timed out: {url}") from e
            
        except httpx.NetworkError as e:
            self.logger.error(f"Network error for URL: {url}", error=str(e))
            raise AdapterConnectionError(f"Network error: {url}") from e
            
        except Exception as e:
            self.logger.error(f"Unexpected error for URL: {url}", error=str(e))
            raise AdapterConnectionError(f"Request failed: {str(e)}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        reraise=True
    )
    async def _get_with_retry(
        self,
        url: str,
        params: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        timeout: int
    ) -> httpx.Response:
        """Internal GET with retry decorator."""
        self.logger.debug(f"GET request to: {url}", params=params)
        return await self.client.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException)),
        reraise=True
    )
    async def _post_with_retry(
        self,
        url: str,
        data: Optional[Dict[str, Any]],
        json: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        timeout: int
    ) -> httpx.Response:
        """Internal POST with retry decorator."""
        self.logger.debug(f"POST request to: {url}")
        return await self.client.post(
            url,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout
        )

    async def _process_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Process HTTP response and handle errors.
        
        Args:
            response: httpx Response object
            
        Returns:
            Response data as dictionary
            
        Raises:
            AdapterRateLimitError: Rate limit exceeded (429)
            AdapterResponseError: Other HTTP errors
        """
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            self.logger.warning(
                f"Rate limit exceeded",
                status_code=429,
                retry_after=retry_after
            )
            raise AdapterRateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after)
            )
        
        # Check for other errors
        if response.status_code >= 400:
            self.logger.error(
                f"HTTP error response",
                status_code=response.status_code,
                url=str(response.url)
            )
            raise AdapterResponseError(
                f"HTTP {response.status_code}: {response.reason_phrase}",
                status_code=response.status_code
            )
        
        # Try to parse JSON
        try:
            return response.json()
        except Exception as e:
            # If not JSON, return text wrapped in dict
            self.logger.warning(f"Non-JSON response received", error=str(e))
            return {"content": response.text}

    async def _wait_for_rate_limit(self, url: str) -> None:
        """Wait if rate limit is exceeded."""
        if self.rate_limiter:
            identifier = self._get_domain_from_url(url)
            allowed = await self.rate_limiter.acquire(identifier)
            
            if not allowed:
                self.logger.warning(f"Rate limit reached for: {identifier}")
                # Wait a bit and retry
                await asyncio.sleep(1)

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            "User-Agent": "ResearchAPI/2.0 (Academic Research Tool)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        }

    @staticmethod
    def _get_domain_from_url(url: str) -> str:
        """Extract domain from URL for rate limiting."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        await self.client.aclose()
        self.logger.info("HTTP client closed")

    @asynccontextmanager
    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
