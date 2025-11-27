"""
FastAPI dependencies for search endpoints.

This module provides dependency injection for services and clients.
"""

from typing import AsyncGenerator
import logging

from researchapi.infrastructure.clients.http_client import HTTPClient
from researchapi.application.services.search_service import SearchService
from researchapi.application.services.article_service import ArticleService
from researchapi.infrastructure.config.settings import get_settings
from researchapi.infrastructure.adapters.arxvi_adapter import ArxivAdapter
from fastapi import Depends

logger = logging.getLogger(__name__)


# ============================================================================
# Infrastructure Dependencies
# ============================================================================

async def get_http_client() -> AsyncGenerator[HTTPClient, None]:
    """
    Provide HTTP client instance with proper lifecycle management.
    
    Yields:
        HTTPClient instance
    """
    settings = get_settings()
    
    client = HTTPClient(
        timeout=getattr(settings, 'http_timeout', 30.0),
        max_retries=getattr(settings, 'http_max_retries', 3),
        logger=logger
    )
    
    try:
        yield client
    finally:
        await client.close()


async def get_arxiv_adapter(
    http_client: HTTPClient = Depends(get_http_client)
) -> ArxivAdapter:
    """
    Provide ArXiv adapter instance.
    
    Args:
        http_client: Injected HTTP client
        
    Returns:
        ArxivAdapter instance
    """
    settings = get_settings()
    
    return ArxivAdapter(
        http_client=http_client,
        logger=logger,
        delay_between_requests=getattr(settings, 'arxiv_delay', 3.0)
    )


# ============================================================================
# Service Dependencies
# ============================================================================

async def get_search_service(
    arxiv_adapter: ArxivAdapter = Depends(get_arxiv_adapter)
) -> SearchService:
    """
    Provide search service instance.
    
    Args:
        arxiv_adapter: Injected ArXiv adapter
        
    Returns:
        SearchService instance
    """
    # TODO: Inject other adapters as they're implemented
    return SearchService(
        arxiv_adapter=arxiv_adapter,
        logger=logger
    )


async def get_article_service(
    arxiv_adapter: ArxivAdapter = Depends(get_arxiv_adapter)
) -> ArticleService:
    """
    Provide article service instance.
    
    Args:
        arxiv_adapter: Injected ArXiv adapter
        
    Returns:
        ArticleService instance
    """
    return ArticleService(
        arxiv_adapter=arxiv_adapter,
        logger=logger
    )

