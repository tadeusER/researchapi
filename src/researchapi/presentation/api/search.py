"""
Search API endpoints - Refactored version.

This module only handles HTTP layer concerns (request/response).
Business logic is delegated to the service layer.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, Depends

from .schemas import SearchResponse, ArticleResponse
from .dependencies import (
    get_search_service,
    get_article_service
)
from researchapi.application.services.search_service import SearchService
from researchapi.application.services.article_service import ArticleService


router = APIRouter()



@router.get("/search", response_model=SearchResponse)
async def search_articles(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    sources: Optional[List[str]] = Query(
        default=None,
        description="Sources to search (arxiv, cambridge, ieee, springer)"
    ),
    max_results: int = Query(default=10, ge=1, le=100),
    year_from: Optional[int] = Query(default=None, ge=1900, le=2100),
    year_to: Optional[int] = Query(default=None, ge=1900, le=2100),
    author: Optional[str] = Query(default=None, description="Filter by author name"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search for academic articles across multiple sources.
    
    Examples:
        - /search?q=quantum+computing&max_results=5
        - /search?q=machine+learning&sources=arxiv&category=cs.LG
        - /search?q=neural+networks&author=Hinton&year_from=2020
    """
    try:
        result = await search_service.search_multi_source(
            query=q,
            sources=sources,
            max_results=max_results,
            year_from=year_from,
            year_to=year_to,
            author=author,
            category=category
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/search/arxiv", response_model=SearchResponse)
async def search_arxiv(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    max_results: int = Query(default=10, ge=1, le=100),
    year_from: Optional[int] = Query(default=None, ge=1900, le=2100),
    year_to: Optional[int] = Query(default=None, ge=1900, le=2100),
    author: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    offset: int = Query(default=0, ge=0),
    sort_by: Optional[str] = Query(default=None),
    sort_order: Optional[str] = Query(default="desc"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search arXiv exclusively with advanced options.
    
    Examples:
        - /search/arxiv?q=transformers&category=cs.CL&max_results=20
        - /search/arxiv?q=reinforcement+learning&author=Sutton
    """
    try:
        result = await search_service.search_arxiv(
            query=q,
            max_results=max_results,
            year_from=year_from,
            year_to=year_to,
            author=author,
            category=category,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ArXiv search error: {str(e)}")


# ============================================================================
# Article Endpoints
# ============================================================================

@router.get("/article/{source}/{article_id}", response_model=ArticleResponse)
async def get_article(
    source: str,
    article_id: str,
    article_service: ArticleService = Depends(get_article_service)
):
    """
    Retrieve a specific article by ID from a source.
    
    Examples:
        - /article/arxiv/1706.03762
        - /article/arxiv/2301.12345v1
    """
    try:
        article = await article_service.get_article(source, article_id)
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail=f"Article not found: {article_id}"
            )
        
        return article
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving article: {str(e)}")


# ============================================================================
# Metadata Endpoints
# ============================================================================

@router.get("/sources")
async def list_sources(
    search_service: SearchService = Depends(get_search_service)
):
    """List all available sources and their status."""
    return await search_service.list_sources()


@router.get("/categories/arxiv")
async def list_arxiv_categories():
    """List popular arXiv categories."""
    return {
        "categories": {
            "computer_science": {
                "cs.AI": "Artificial Intelligence",
                "cs.CL": "Computation and Language",
                "cs.CV": "Computer Vision and Pattern Recognition",
                "cs.LG": "Machine Learning",
                "cs.NE": "Neural and Evolutionary Computing",
                "cs.RO": "Robotics",
                "cs.CR": "Cryptography and Security",
            },
            "physics": {
                "quant-ph": "Quantum Physics",
                "physics.comp-ph": "Computational Physics",
            },
            "mathematics": {
                "math.ST": "Statistics Theory",
                "math.OC": "Optimization and Control",
            },
        },
        "documentation": "https://arxiv.org/category_taxonomy"
    }