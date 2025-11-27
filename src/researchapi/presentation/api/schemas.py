"""
API schemas (DTOs) for search endpoints.

This module contains all Pydantic models used for request/response serialization.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


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
    categories: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1706.03762",
                "title": "Attention is All You Need",
                "source": "arxiv",
                "doi": None,
                "url": "http://arxiv.org/abs/1706.03762",
                "pdf_url": "http://arxiv.org/pdf/1706.03762",
                "abstract": "The dominant sequence transduction models...",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "publication_year": 2017,
                "journal": "NIPS 2017",
                "keywords": [],
                "categories": ["cs.CL", "cs.LG"]
            }
        }


class SearchResponse(BaseModel):
    """Search response model for API."""
    query: str
    total_results: int
    results: List[ArticleResponse]
    sources: List[str]
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "quantum computing",
                "total_results": 1523,
                "results": [],
                "sources": ["arxiv"],
                "execution_time": 1.23,
                "timestamp": "2024-11-26T12:00:00Z"
            }
        }


class SourceInfo(BaseModel):
    """Information about a data source."""
    name: str
    enabled: bool
    requires_api_key: bool
    description: str
    configured: Optional[bool] = None
    features: Optional[List[str]] = None
    status: Optional[str] = None


class SourcesResponse(BaseModel):
    """Response for listing sources."""
    sources: List[SourceInfo]
    total: int
    enabled: int