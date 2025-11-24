"""
Search API endpoints.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from core.entities import SourceType


router = APIRouter()


class ArticleResponse(BaseModel):
    """Article response model for API."""
    id: Optional[str]
    title: str
    source: str
    doi: Optional[str]
    url: Optional[str]
    pdf_url: Optional[str]
    abstract: Optional[str]
    authors: List[str]
    publication_year: Optional[int]
    journal: Optional[str]
    keywords: List[str] = []


class SearchResponse(BaseModel):
    """Search response model for API."""
    query: str
    total_results: int
    results: List[ArticleResponse]
    sources: List[str]
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


@router.get("/search", response_model=SearchResponse)
async def search_articles(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    sources: Optional[List[str]] = Query(
        default=None,
        description="Sources to search (arxiv, cambridge, ieee, springer)"
    ),
    max_results: int = Query(default=10, ge=1, le=100, description="Maximum results per source"),
    year_from: Optional[int] = Query(default=None, ge=1900, le=2100),
    year_to: Optional[int] = Query(default=None, ge=1900, le=2100),
):
    """
    Search for academic articles across multiple sources.
    
    Args:
        q: Search query string
        sources: List of sources to search (default: all enabled sources)
        max_results: Maximum number of results per source
        year_from: Filter articles from this year onwards
        year_to: Filter articles up to this year
        
    Returns:
        SearchResponse with articles from all sources
    """
    # This is a placeholder - actual implementation would use the service layer
    return SearchResponse(
        query=q,
        total_results=0,
        results=[],
        sources=sources or ["arxiv", "cambridge", "ieee", "springer"],
        execution_time=0.0
    )


@router.get("/article/{source}/{article_id}", response_model=ArticleResponse)
async def get_article(
    source: str,
    article_id: str
):
    """
    Retrieve a specific article by ID from a source.
    
    Args:
        source: Source name (arxiv, cambridge, ieee, springer)
        article_id: Article identifier in the source system
        
    Returns:
        ArticleResponse with article details
    """
    # Validate source
    try:
        SourceType(source.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source: {source}. Must be one of: arxiv, cambridge, ieee, springer"
        )
    
    # Placeholder implementation
    raise HTTPException(
        status_code=501,
        detail="Article retrieval not yet implemented"
    )


@router.get("/sources")
async def list_sources():
    """
    List all available sources and their status.
    
    Returns:
        Dictionary with source information
    """
    from infrastructure.config.settings import get_settings
    
    settings = get_settings()
    
    return {
        "sources": [
            {
                "name": "arxiv",
                "enabled": settings.features.arxiv_enabled,
                "requires_api_key": False,
                "description": "arXiv preprint repository"
            },
            {
                "name": "cambridge",
                "enabled": settings.features.cambridge_enabled,
                "requires_api_key": False,
                "description": "Cambridge University Press"
            },
            {
                "name": "ieee",
                "enabled": settings.features.ieee_enabled,
                "requires_api_key": True,
                "configured": settings.api_keys.ieee_api_key is not None,
                "description": "IEEE Xplore Digital Library"
            },
            {
                "name": "springer",
                "enabled": settings.features.springer_enabled,
                "requires_api_key": True,
                "configured": settings.api_keys.springer_api_key is not None,
                "description": "Springer Nature"
            }
        ]
    }
