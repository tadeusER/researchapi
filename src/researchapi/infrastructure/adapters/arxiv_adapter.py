"""
arXiv adapter implementation.

Implements the IArticleAdapter interface for arXiv API.
"""

import xml.etree.ElementTree as ET
from typing import Optional, List
from datetime import datetime
import asyncio

from core.interfaces import IArticleAdapter, IHTTPClient, ILogger
from core.entities import Article, Author, SearchQuery, SearchResult, SourceType
from core.exceptions import AdapterException, AdapterParsingError, AdapterTimeoutError
from adapters.base_adapter import BaseAdapter


class ArxivAdapter(BaseAdapter):
    """
    Adapter for arXiv API.
    
    Implements search and retrieval of academic articles from arXiv.org
    using their Atom-based REST API.
    """
    
    # XML namespaces used by arXiv API
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    # API endpoint
    API_BASE_URL = "http://export.arxiv.org/api"
    
    # Rate limiting: arXiv recommends 3 seconds between requests
    DEFAULT_DELAY = 3.0
    
    # Maximum results per request (arXiv limit)
    MAX_RESULTS_PER_REQUEST = 2000
    
    def __init__(
        self,
        http_client: IHTTPClient,
        logger: ILogger,
        delay_between_requests: float = DEFAULT_DELAY
    ):
        """
        Initialize arXiv adapter.
        
        Args:
            http_client: HTTP client instance
            logger: Logger instance
            delay_between_requests: Delay in seconds between requests (default: 3.0)
        """
        super().__init__(
            http_client=http_client,
            logger=logger,
            source_type=SourceType.ARXIV,
            base_url=self.API_BASE_URL,
            delay_between_requests=delay_between_requests
        )

    async def search(self, query: SearchQuery) -> SearchResult:
        """
        Search for articles on arXiv.
        
        Args:
            query: SearchQuery object containing search parameters
            
        Returns:
            SearchResult containing articles and metadata
            
        Raises:
            AdapterException: If search fails
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Build search parameters
            params = self._build_search_params(query)
            
            # Log the search
            self._logger.info(
                f"Searching arXiv",
                query=query.query,
                max_results=query.max_results,
                source=self._source_type.value
            )
            
            # Make the request
            url = self._build_url("query")
            response_text = await self._make_request(url, params)
            
            # Parse the Atom response
            articles, total_results = self._parse_atom_response(response_text)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Determine if there are more results
            has_more = (query.start_index + len(articles)) < total_results
            next_start_index = query.start_index + len(articles) if has_more else None
            
            self._logger.info(
                f"arXiv search completed",
                count=len(articles),
                total=total_results,
                execution_time=f"{execution_time:.2f}s"
            )
            
            return SearchResult(
                query=query,
                articles=articles,
                total_results=total_results,
                source=self._source_type,
                execution_time=execution_time,
                has_more=has_more,
                next_start_index=next_start_index
            )
            
        except Exception as e:
            await self._handle_adapter_error(e, "search")

    async def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve a single article by its arXiv ID.
        
        Args:
            article_id: arXiv identifier (e.g., "2301.00001" or "hep-th/9901001")
            
        Returns:
            Article if found, None otherwise
            
        Raises:
            AdapterException: If retrieval fails
        """
        try:
            # Apply rate limiting
            await self._apply_rate_limit()
            
            self._logger.info(
                f"Fetching article from arXiv",
                article_id=article_id,
                source=self._source_type.value
            )
            
            # Build parameters for id_list query
            params = {
                "id_list": article_id,
                "max_results": 1
            }
            
            # Make the request
            url = self._build_url("query")
            response_text = await self._make_request(url, params)
            
            # Parse the response
            articles, total_results = self._parse_atom_response(response_text)
            
            if not articles:
                self._logger.warning(
                    f"Article not found on arXiv",
                    article_id=article_id
                )
                return None
            
            self._logger.info(
                f"Article retrieved from arXiv",
                article_id=article_id,
                title=articles[0].title
            )
            
            return articles[0]
            
        except Exception as e:
            await self._handle_adapter_error(e, f"get_article({article_id})")

    async def health_check(self) -> bool:
        """
        Check if arXiv API is responding.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self._logger.debug("Performing arXiv health check")
            
            # Try a simple query
            params = {
                "search_query": "all:test",
                "max_results": 1
            }
            
            url = self._build_url("query")
            await self._make_request(url, params)
            
            self._logger.info("arXiv health check passed")
            return True
            
        except Exception as e:
            self._logger.error(
                f"arXiv health check failed",
                error=str(e)
            )
            return False

    def _build_search_params(self, query: SearchQuery) -> dict:
        """
        Build URL parameters for arXiv API query.
        
        Args:
            query: SearchQuery object
            
        Returns:
            Dictionary of query parameters
        """
        params = {
            "search_query": self._build_search_query(query),
            "start": query.start_index,
            "max_results": min(query.max_results, self.MAX_RESULTS_PER_REQUEST)
        }
        
        # Add sorting if specified
        if query.sort_by:
            sort_by_mapping = {
                "relevance": "relevance",
                "date": "submittedDate",
                "citations": "submittedDate"  # arXiv doesn't support citation sorting
            }
            params["sortBy"] = sort_by_mapping.get(query.sort_by, "relevance")
            
            sort_order_mapping = {
                "asc": "ascending",
                "desc": "descending"
            }
            params["sortOrder"] = sort_order_mapping.get(query.sort_order, "descending")
        
        return params

    def _build_search_query(self, query: SearchQuery) -> str:
        """
        Build arXiv search query string.
        
        Args:
            query: SearchQuery object
            
        Returns:
            Formatted search query string
        """
        search_parts = []
        
        # Main query
        if query.query:
            search_parts.append(f"all:{query.query}")
        
        # Author filter
        if query.authors:
            author_queries = [f"au:{author}" for author in query.authors]
            search_parts.append(f"({' OR '.join(author_queries)})")
        
        # Category filter
        if query.categories:
            category_queries = [f"cat:{cat}" for cat in query.categories]
            search_parts.append(f"({' OR '.join(category_queries)})")
        
        # Date range filter
        if query.year_from or query.year_to:
            year_from = query.year_from or 1991  # arXiv started in 1991
            year_to = query.year_to or datetime.now().year
            
            # Format: submittedDate:[YYYYMMDD+TO+YYYYMMDD]
            date_from = f"{year_from}0101"
            date_to = f"{year_to}1231"
            search_parts.append(f"submittedDate:[{date_from}+TO+{date_to}]")
        
        # Combine all parts with AND
        if not search_parts:
            return "all:*"  # Return all if no query specified
        
        return " AND ".join(search_parts)

    async def _make_request(self, url: str, params: dict) -> str:
        """
        Make HTTP request to arXiv API.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            Response text
            
        Raises:
            AdapterException: If request fails
        """
        try:
            response = await self._http_client.get(
                url=url,
                params=params,
                timeout=30
            )
            
            # arXiv returns text/xml, need to handle as text
            if isinstance(response, dict) and 'text' in response:
                return response['text']
            elif isinstance(response, str):
                return response
            else:
                # If response is dict without text, it might be parsed JSON
                # This shouldn't happen with arXiv, but handle it
                raise AdapterParsingError("Unexpected response format from arXiv")
                
        except AdapterTimeoutError:
            raise
        except Exception as e:
            raise AdapterException(f"Request to arXiv failed: {str(e)}") from e

    def _parse_atom_response(self, xml_text: str) -> tuple[List[Article], int]:
        """
        Parse Atom XML response from arXiv API.
        
        Args:
            xml_text: XML response text
            
        Returns:
            Tuple of (list of articles, total results count)
            
        Raises:
            AdapterParsingError: If parsing fails
        """
        try:
            root = ET.fromstring(xml_text)
            
            # Check for errors
            entries = root.findall('.//atom:entry', self.NAMESPACES)
            if entries and self._is_error_entry(entries[0]):
                error_msg = self._extract_error_message(entries[0])
                raise AdapterException(f"arXiv API error: {error_msg}")
            
            # Get total results
            total_results_elem = root.find('.//opensearch:totalResults', self.NAMESPACES)
            total_results = int(total_results_elem.text) if total_results_elem is not None else 0
            
            # Parse articles
            articles = []
            for entry in entries:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self._logger.warning(
                        f"Failed to parse arXiv entry",
                        error=str(e)
                    )
                    continue
            
            return articles, total_results
            
        except ET.ParseError as e:
            raise AdapterParsingError(f"Failed to parse arXiv XML response: {str(e)}") from e
        except Exception as e:
            if isinstance(e, AdapterException):
                raise
            raise AdapterParsingError(f"Error parsing arXiv response: {str(e)}") from e

    def _is_error_entry(self, entry: ET.Element) -> bool:
        """Check if entry represents an error."""
        entry_id = entry.find('atom:id', self.NAMESPACES)
        if entry_id is not None and 'api/errors' in entry_id.text:
            return True
        return False

    def _extract_error_message(self, entry: ET.Element) -> str:
        """Extract error message from error entry."""
        summary = entry.find('atom:summary', self.NAMESPACES)
        return summary.text if summary is not None else "Unknown error"

    def _parse_entry(self, entry: ET.Element) -> Optional[Article]:
        """
        Parse a single Atom entry into an Article.
        
        Args:
            entry: XML entry element
            
        Returns:
            Article object or None if parsing fails
        """
        try:
            # Extract basic fields
            title_elem = entry.find('atom:title', self.NAMESPACES)
            title = self._clean_text(title_elem.text) if title_elem is not None else None
            
            if not title:
                return None
            
            # Extract ID (format: http://arxiv.org/abs/XXXX.XXXXX)
            id_elem = entry.find('atom:id', self.NAMESPACES)
            article_id = None
            url = None
            if id_elem is not None:
                url = id_elem.text
                article_id = url.replace('http://arxiv.org/abs/', '')
            
            # Extract dates
            published_elem = entry.find('atom:published', self.NAMESPACES)
            updated_elem = entry.find('atom:updated', self.NAMESPACES)
            
            publication_date = self._parse_date(published_elem.text) if published_elem is not None else None
            updated_date = self._parse_date(updated_elem.text) if updated_elem is not None else None
            
            # Extract abstract
            summary_elem = entry.find('atom:summary', self.NAMESPACES)
            abstract = self._clean_text(summary_elem.text) if summary_elem is not None else None
            
            # Extract authors
            authors = self._parse_authors(entry)
            
            # Extract categories
            categories = self._parse_categories(entry)
            
            # Extract primary category
            primary_category_elem = entry.find('arxiv:primary_category', self.NAMESPACES)
            primary_category = None
            if primary_category_elem is not None:
                primary_category = primary_category_elem.get('term')
            
            # Extract links
            pdf_url = None
            doi = None
            for link in entry.findall('atom:link', self.NAMESPACES):
                title_attr = link.get('title')
                if title_attr == 'pdf':
                    pdf_url = link.get('href')
                elif title_attr == 'doi':
                    doi = link.get('href')
                    # Extract DOI from URL
                    if doi and 'doi.org/' in doi:
                        doi = doi.split('doi.org/')[-1]
            
            # Extract arXiv-specific metadata
            comment_elem = entry.find('arxiv:comment', self.NAMESPACES)
            comment = comment_elem.text if comment_elem is not None else None
            
            journal_ref_elem = entry.find('arxiv:journal_ref', self.NAMESPACES)
            journal_ref = journal_ref_elem.text if journal_ref_elem is not None else None
            
            arxiv_doi_elem = entry.find('arxiv:doi', self.NAMESPACES)
            if arxiv_doi_elem is not None and not doi:
                doi = arxiv_doi_elem.text
            
            # Create Article
            article = Article(
                id=article_id,
                title=title,
                source=SourceType.ARXIV,
                url=url,
                pdf_url=pdf_url,
                doi=doi,
                abstract=abstract,
                authors=authors,
                publication_date=publication_date or updated_date,
                publication_year=publication_date.year if publication_date else None,
                categories=categories if primary_category else [],
                subjects=[primary_category] if primary_category else [],
                journal=journal_ref,
                updated_at=updated_date or datetime.utcnow()
            )
            
            # Store comment in raw_data if present
            if comment:
                article.raw_data = {'comment': comment}
            
            return article
            
        except Exception as e:
            self._logger.warning(
                f"Error parsing arXiv entry",
                error=str(e),
                error_type=type(e).__name__
            )
            return None

    def _parse_authors(self, entry: ET.Element) -> List[Author]:
        """
        Parse authors from entry.
        
        Args:
            entry: XML entry element
            
        Returns:
            List of Author objects
        """
        authors = []
        
        for author_elem in entry.findall('atom:author', self.NAMESPACES):
            name_elem = author_elem.find('atom:name', self.NAMESPACES)
            if name_elem is None:
                continue
            
            name = self._clean_text(name_elem.text)
            
            # Extract affiliation if present
            affiliation_elem = author_elem.find('arxiv:affiliation', self.NAMESPACES)
            affiliation = affiliation_elem.text if affiliation_elem is not None else None
            
            authors.append(Author(
                name=name,
                affiliation=affiliation
            ))
        
        return authors

    def _parse_categories(self, entry: ET.Element) -> List[str]:
        """
        Parse categories from entry.
        
        Args:
            entry: XML entry element
            
        Returns:
            List of category strings
        """
        categories = []
        
        for category_elem in entry.findall('atom:category', self.NAMESPACES):
            term = category_elem.get('term')
            if term and term.startswith(('cs.', 'math.', 'physics.', 'q-bio.', 
                                         'q-fin.', 'stat.', 'eess.', 'econ.')):
                categories.append(term)
        
        return categories

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """
        Parse ISO format date string.
        
        Args:
            date_string: ISO format date string
            
        Returns:
            datetime object or None
        """
        try:
            # arXiv uses ISO 8601 format
            # Example: 2003-07-07T13:46:39-04:00
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None

    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing extra whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text or None
        """
        if not text:
            return None
        
        # Replace multiple whitespace with single space
        import re
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()
