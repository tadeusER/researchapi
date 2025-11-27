"""
Search service - Business logic layer.

This service orchestrates search operations across multiple sources
and handles business rules.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import logging

from researchapi.core.entities import SearchQuery, Article, SourceType
from researchapi.core.exceptions import SearchException
from researchapi.infrastructure.adapters.arxvi_adapter import ArxivAdapter
from researchapi.infrastructure.config.settings import get_settings
from researchapi.presentation.api.schemas import SearchResponse, ArticleResponse


class SearchService:
    """
    Service for orchestrating article searches across multiple sources.
    
    This service handles:
    - Multi-source search coordination
    - Business logic and validation
    - Response formatting
    - Error handling and logging
    """
    
    def __init__(
        self,
        arxiv_adapter: ArxivAdapter,
        logger: logging.Logger
    ):
        """
        Initialize search service.
        
        Args:
            arxiv_adapter: ArXiv adapter instance
            logger: Logger instance
        """
        self.arxiv_adapter = arxiv_adapter
        self.logger = logger
        self.settings = get_settings()
    
    async def search_multi_source(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        author: Optional[str] = None,
        category: Optional[str] = None
    ) -> SearchResponse:
        """
        Search across multiple sources.
        
        Args:
            query: Search query string
            sources: List of sources to search (None = all enabled)
            max_results: Maximum results per source
            year_from: Start year filter
            year_to: End year filter
            author: Author filter
            category: Category filter
            
        Returns:
            SearchResponse with combined results
            
        Raises:
            ValueError: If parameters are invalid
            SearchException: If search fails
        """
        start_time = time.time()
        
        # Determine sources to search
        sources_to_search = self._determine_sources(sources)
        
        all_articles = []
        total_results = 0
        searched_sources = []
        
        # Search each enabled source
        if "arxiv" in sources_to_search and self.settings.features.arxiv_enabled:
            try:
                articles, arxiv_total = await self._search_arxiv(
                    query=query,
                    max_results=max_results,
                    year_from=year_from,
                    year_to=year_to,
                    author=author,
                    category=category
                )
                all_articles.extend(articles)
                total_results += arxiv_total
                searched_sources.append("arxiv")
                
            except Exception as e:
                self.logger.error(f"ArXiv search failed: {str(e)}")
                # Continue with other sources
        
        # TODO: Add other sources
        
        # Convert to response format
        results = [self._article_to_response(a) for a in all_articles]
        
        execution_time = time.time() - start_time
        
        return SearchResponse(
            query=query,
            total_results=total_results,
            results=results,
            sources=searched_sources,
            execution_time=execution_time
        )
    
    async def search_arxiv(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        author: Optional[str] = None,
        category: Optional[str] = None,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ) -> SearchResponse:
        """
        Search arXiv exclusively with advanced options.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            year_from: Start year filter
            year_to: End year filter
            author: Author filter
            category: Category filter
            offset: Pagination offset
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            
        Returns:
            SearchResponse with arXiv results
        """
        start_time = time.time()
        
        # Build domain search query
        start_date = None
        end_date = None
        
        if year_from:
            start_date = datetime(year_from, 1, 1)
        if year_to:
            end_date = datetime(year_to, 12, 31, 23, 59, 59)
        
        domain_query = SearchQuery(
            keywords=query.split(),
            author=author,
            category=category,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Perform search
        self.logger.info(f"ArXiv search: query='{query}', category={category}, offset={offset}")
        
        result = await self.arxiv_adapter.search(domain_query)
        
        # Convert to response format
        results = [self._article_to_response(a) for a in result.articles]
        
        execution_time = time.time() - start_time
        
        self.logger.info(
            f"ArXiv search completed: "
            f"total={result.total_results}, "
            f"returned={len(results)}, "
            f"time={execution_time:.2f}s"
        )
        
        return SearchResponse(
            query=query,
            total_results=result.total_results,
            results=results,
            sources=["arxiv"],
            execution_time=execution_time
        )
    
    async def list_sources(self) -> Dict[str, Any]:
        """
        List all available sources and their status.
        
        Returns:
            Dictionary with source information
        """
        sources_info = [
            {
                "name": "arxiv",
                "enabled": self.settings.features.arxiv_enabled,
                "requires_api_key": False,
                "description": "arXiv preprint repository",
                "categories": ["cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.NE"],
                "features": ["search", "get_by_id", "date_filter", "category_filter", "author_filter"]
            },
            {
                "name": "cambridge",
                "enabled": self.settings.features.cambridge_enabled,
                "requires_api_key": False,
                "description": "Cambridge University Press",
                "status": "not_implemented"
            },
            {
                "name": "ieee",
                "enabled": self.settings.features.ieee_enabled,
                "requires_api_key": True,
                "configured": self.settings.api_keys.ieee_api_key is not None,
                "description": "IEEE Xplore Digital Library",
                "status": "not_implemented"
            },
            {
                "name": "springer",
                "enabled": self.settings.features.springer_enabled,
                "requires_api_key": True,
                "configured": self.settings.api_keys.springer_api_key is not None,
                "description": "Springer Nature",
                "status": "not_implemented"
            }
        ]
        
        return {
            "sources": sources_info,
            "total": len(sources_info),
            "enabled": sum(1 for s in sources_info if s["enabled"])
        }
    
    # ========================================================================
    # Private Helper Methods
    # ========================================================================
    
    def _determine_sources(self, sources: Optional[List[str]]) -> List[str]:
        """Determine which sources to search based on input and configuration."""
        if sources is None:
            # Default to all enabled sources
            enabled = []
            if self.settings.features.arxiv_enabled:
                enabled.append("arxiv")
            if self.settings.features.cambridge_enabled:
                enabled.append("cambridge")
            if self.settings.features.ieee_enabled:
                enabled.append("ieee")
            if self.settings.features.springer_enabled:
                enabled.append("springer")
            return enabled
        
        # Validate requested sources
        sources = [s.lower() for s in sources]
        valid_sources = {"arxiv", "cambridge", "ieee", "springer"}
        invalid = set(sources) - valid_sources
        
        if invalid:
            raise ValueError(
                f"Invalid sources: {invalid}. Must be one of: {valid_sources}"
            )
        
        return sources
    
    async def _search_arxiv(
        self,
        query: str,
        max_results: int,
        year_from: Optional[int],
        year_to: Optional[int],
        author: Optional[str],
        category: Optional[str]
    ) -> tuple[List[Article], int]:
        """Execute arXiv search and return results."""
        start_date = None
        end_date = None
        
        if year_from:
            start_date = datetime(year_from, 1, 1)
        if year_to:
            end_date = datetime(year_to, 12, 31, 23, 59, 59)
        
        domain_query = SearchQuery(
            keywords=query.split(),
            author=author,
            category=category,
            start_date=start_date,
            end_date=end_date,
            max_results=max_results,
            offset=0
        )
        
        self.logger.info(f"Searching arXiv: query='{query}', max_results={max_results}")
        
        result = await self.arxiv_adapter.search(domain_query)
        
        self.logger.info(
            f"ArXiv search completed: "
            f"found {result.total_results} total, "
            f"returned {len(result.articles)} articles"
        )
        
        return result.articles, result.total_results
    
    def _article_to_response(self, article: Article) -> ArticleResponse:
        """Convert domain Article entity to API response DTO."""
        return ArticleResponse(
            id=article.id,
            title=article.title,
            source=article.source.value,
            doi=article.doi,
            url=article.url,
            pdf_url=article.pdf_url,
            abstract=article.abstract,
            authors=[author.name for author in article.authors],
            publication_year=article.published_date.year if article.published_date else None,
            journal=article.metadata.get('journal_reference') if article.metadata else None,
            keywords=article.keywords,
            categories=article.categories
        )