"""
Article service - Business logic for article operations.

This service handles operations related to individual articles.
"""

from typing import Optional
import logging

from researchapi.core.entities import Article, SourceType
from researchapi.core.exceptions import FetchException
from researchapi.infrastructure.adapters.arxvi_adapter import ArxivAdapter
from researchapi.presentation.api.schemas import ArticleResponse


class ArticleService:
    """
    Service for article-related operations.
    
    This service handles:
    - Fetching individual articles
    - Validating article requests
    - Response formatting
    """
    
    def __init__(
        self,
        arxiv_adapter: ArxivAdapter,
        logger: logging.Logger
    ):
        """
        Initialize article service.
        
        Args:
            arxiv_adapter: ArXiv adapter instance
            logger: Logger instance
        """
        self.arxiv_adapter = arxiv_adapter
        self.logger = logger
    
    async def get_article(
        self,
        source: str,
        article_id: str
    ) -> Optional[ArticleResponse]:
        """
        Retrieve a specific article by ID from a source.
        
        Args:
            source: Source name (arxiv, cambridge, ieee, springer)
            article_id: Article identifier
            
        Returns:
            ArticleResponse if found, None otherwise
            
        Raises:
            ValueError: If source is invalid
            FetchException: If retrieval fails
        """
        # Validate source
        try:
            source_type = SourceType(source.lower())
        except ValueError:
            raise ValueError(
                f"Invalid source: {source}. "
                f"Must be one of: arxiv, cambridge, ieee, springer"
            )
        
        # Get article from appropriate source
        if source_type == SourceType.ARXIV:
            self.logger.info(f"Fetching arXiv article: {article_id}")
            
            article = await self.arxiv_adapter.get_article(article_id)
            
            if not article:
                self.logger.warning(f"ArXiv article not found: {article_id}")
                return None
            
            self.logger.info(f"ArXiv article retrieved: {article_id}")
            return self._article_to_response(article)
        
        else:
            # Other sources not yet implemented
            raise ValueError(
                f"Article retrieval from {source} not yet implemented"
            )
    
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