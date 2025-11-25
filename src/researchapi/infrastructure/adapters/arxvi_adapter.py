"""
ArXiv adapter implementation for searching and retrieving academic articles.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

from core.interfaces import IHTTPClient
from core.entities import Article, SearchQuery, SearchResult, SourceType, Author
from core.exceptions import AdapterException
from adapters.base_adapter import BaseAdapter
import logging


class ArxivAdapter(BaseAdapter):
    """
    Adapter for arXiv API.
    
    Implements search and retrieval functionality for arXiv e-prints.
    API Documentation: https://arxiv.org/help/api/user-manual
    """
    
    # arXiv API constants
    ARXIV_API_BASE_URL = "http://export.arxiv.org/api"
    DEFAULT_MAX_RESULTS = 10
    MAX_RESULTS_PER_REQUEST = 2000
    ABSOLUTE_MAX_RESULTS = 30000
    RECOMMENDED_DELAY = 3.0  # seconds between requests as per API guidelines
    
    # XML namespaces
    NAMESPACES = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom',
        'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
    }
    
    # Field prefixes for search queries
    SEARCH_FIELDS = {
        'title': 'ti',
        'author': 'au',
        'abstract': 'abs',
        'comment': 'co',
        'journal_ref': 'jr',
        'category': 'cat',
        'report_number': 'rn',
        'all': 'all'
    }
    
    # Sort options
    SORT_BY = {
        'relevance': 'relevance',
        'last_updated': 'lastUpdatedDate',
        'submitted': 'submittedDate'
    }
    
    SORT_ORDER = {
        'ascending': 'ascending',
        'descending': 'descending'
    }

    def __init__(
        self,
        http_client: IHTTPClient,
        logger: logging.Logger,
        delay_between_requests: float = RECOMMENDED_DELAY
    ):
        """
        Initialize ArXiv adapter.
        
        Args:
            http_client: HTTP client instance
            logger: Logger instance
            delay_between_requests: Delay in seconds between requests (default: 3s as recommended)
        """
        super().__init__(
            http_client=http_client,
            logger=logger,
            source_type=SourceType.ARXIV,
            base_url=self.ARXIV_API_BASE_URL,
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
            AdapterException: If the search fails
        """
        try:
            await self._apply_rate_limit()
            
            # Build search query string
            search_query_str = self._build_search_query(query)
            
            # Build URL parameters
            params = {
                'search_query': search_query_str,
                'start': query.offset or 0,
                'max_results': min(
                    query.max_results or self.DEFAULT_MAX_RESULTS,
                    self.MAX_RESULTS_PER_REQUEST
                )
            }
            
            # Add sorting parameters if specified
            if query.sort_by:
                sort_by = self._map_sort_field(query.sort_by)
                if sort_by:
                    params['sortBy'] = sort_by
                    params['sortOrder'] = self._map_sort_order(query.sort_order)
            
            # Make API request
            url = self._build_url("query")
            self._logger.info(
                f"Searching arXiv",
                query=search_query_str,
                start=params['start'],
                max_results=params['max_results']
            )
            
            response = await self._http_client.get(url, params=params)
            
            # Parse response
            articles, total_results = self._parse_atom_feed(response)
            
            self._logger.info(
                f"ArXiv search completed",
                results_count=len(articles),
                total_results=total_results
            )
            
            return SearchResult(
                articles=articles,
                total_results=total_results,
                offset=params['start'],
                source=SourceType.ARXIV,
                query=query
            )
            
        except Exception as e:
            await self._handle_adapter_error(e, "search")

    async def get_article(self, article_id: str) -> Optional[Article]:
        """
        Retrieve a single article by its arXiv ID.
        
        Args:
            article_id: arXiv identifier (e.g., "2301.12345" or "hep-ex/0307015")
            
        Returns:
            Article if found, None otherwise
            
        Raises:
            AdapterException: If the retrieval fails
        """
        try:
            await self._apply_rate_limit()
            
            # Clean the article ID (remove version if present for search)
            clean_id = article_id.split('v')[0] if 'v' in article_id else article_id
            
            # Build URL with id_list parameter
            url = self._build_url("query")
            params = {
                'id_list': clean_id,
                'max_results': 1
            }
            
            self._logger.info(f"Fetching arXiv article", article_id=clean_id)
            
            response = await self._http_client.get(url, params=params)
            
            # Parse response
            articles, _ = self._parse_atom_feed(response)
            
            if articles:
                self._logger.info(f"ArXiv article found", article_id=clean_id)
                return articles[0]
            else:
                self._logger.warning(f"ArXiv article not found", article_id=clean_id)
                return None
                
        except Exception as e:
            await self._handle_adapter_error(e, f"get_article({article_id})")

    async def health_check(self) -> bool:
        """
        Check if the arXiv API is responding.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            url = self._build_url("query")
            params = {
                'search_query': 'all:test',
                'max_results': 1
            }
            
            response = await self._http_client.get(url, params=params)
            
            # Simple check that we got valid XML
            root = ET.fromstring(response)
            
            self._logger.info("ArXiv health check passed")
            return True
            
        except Exception as e:
            self._logger.error(
                "ArXiv health check failed",
                error=str(e)
            )
            return False

    def _build_search_query(self, query: SearchQuery) -> str:
        """
        Build arXiv search query string from SearchQuery object.
        
        Args:
            query: SearchQuery object
            
        Returns:
            Formatted search query string
        """
        query_parts = []
        
        # Add keyword search
        if query.keywords:
            # Search in all fields if no specific field is specified
            field_prefix = self.SEARCH_FIELDS.get('all', 'all')
            keywords_str = ' '.join(query.keywords)
            query_parts.append(f"{field_prefix}:{keywords_str}")
        
        # Add title search
        if query.title:
            field_prefix = self.SEARCH_FIELDS.get('title', 'ti')
            query_parts.append(f'{field_prefix}:"{query.title}"')
        
        # Add author search
        if query.author:
            field_prefix = self.SEARCH_FIELDS.get('author', 'au')
            query_parts.append(f"{field_prefix}:{query.author}")
        
        # Add abstract search
        if query.abstract:
            field_prefix = self.SEARCH_FIELDS.get('abstract', 'abs')
            query_parts.append(f'{field_prefix}:"{query.abstract}"')
        
        # Add category filter
        if query.category:
            field_prefix = self.SEARCH_FIELDS.get('category', 'cat')
            query_parts.append(f"{field_prefix}:{query.category}")
        
        # Add date range filter using submittedDate
        if query.start_date or query.end_date:
            date_query = self._build_date_query(query.start_date, query.end_date)
            if date_query:
                query_parts.append(date_query)
        
        # Combine all parts with AND
        if not query_parts:
            # Default to searching all fields
            return "all:*"
        
        return " AND ".join(query_parts)

    def _build_date_query(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> str:
        """
        Build date range query for submittedDate.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Date range query string in format [YYYYMMDDTTTT TO YYYYMMDDTTTT]
        """
        if not start_date and not end_date:
            return ""
        
        # Format: YYYYMMDDTTTT (24-hour time to the minute in GMT)
        date_format = "%Y%m%d%H%M"
        
        # Default to wide range if only one date is specified
        start_str = start_date.strftime(date_format) if start_date else "19910701000"
        end_str = end_date.strftime(date_format) if end_date else "99991231235"
        
        return f"submittedDate:[{start_str} TO {end_str}]"

    def _map_sort_field(self, sort_by: str) -> Optional[str]:
        """
        Map generic sort field to arXiv-specific field.
        
        Args:
            sort_by: Generic sort field name
            
        Returns:
            ArXiv sort field name or None
        """
        mapping = {
            'relevance': 'relevance',
            'date': 'lastUpdatedDate',
            'submitted_date': 'submittedDate',
            'updated_date': 'lastUpdatedDate'
        }
        return mapping.get(sort_by.lower(), 'relevance')

    def _map_sort_order(self, sort_order: Optional[str]) -> str:
        """
        Map generic sort order to arXiv-specific order.
        
        Args:
            sort_order: Generic sort order ('asc' or 'desc')
            
        Returns:
            ArXiv sort order ('ascending' or 'descending')
        """
        if not sort_order:
            return 'descending'
        
        order = sort_order.lower()
        if order in ['asc', 'ascending']:
            return 'ascending'
        return 'descending'

    def _parse_atom_feed(self, xml_content: str) -> tuple[List[Article], int]:
        """
        Parse Atom feed XML response from arXiv API.
        
        Args:
            xml_content: XML string from API response
            
        Returns:
            Tuple of (list of Article objects, total results count)
            
        Raises:
            AdapterException: If parsing fails
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Check for errors
            self._check_for_errors(root)
            
            # Get total results from OpenSearch element
            total_results_elem = root.find('opensearch:totalResults', self.NAMESPACES)
            total_results = int(total_results_elem.text) if total_results_elem is not None else 0
            
            # Parse each entry
            articles = []
            entries = root.findall('atom:entry', self.NAMESPACES)
            
            for entry in entries:
                article = self._parse_entry(entry)
                if article:
                    articles.append(article)
            
            return articles, total_results
            
        except ET.ParseError as e:
            raise AdapterException(f"Failed to parse arXiv XML response: {str(e)}")
        except Exception as e:
            raise AdapterException(f"Error processing arXiv response: {str(e)}")

    def _check_for_errors(self, root: ET.Element) -> None:
        """
        Check if the response contains error entries.
        
        Args:
            root: Root XML element
            
        Raises:
            AdapterException: If an error is found
        """
        entries = root.findall('atom:entry', self.NAMESPACES)
        
        for entry in entries:
            entry_id = entry.find('atom:id', self.NAMESPACES)
            if entry_id is not None and 'api/errors' in entry_id.text:
                # This is an error entry
                title = entry.find('atom:title', self.NAMESPACES)
                summary = entry.find('atom:summary', self.NAMESPACES)
                
                error_msg = summary.text if summary is not None else "Unknown error"
                raise AdapterException(f"ArXiv API error: {error_msg}")

    def _parse_entry(self, entry: ET.Element) -> Optional[Article]:
        """
        Parse a single entry element into an Article object.
        
        Args:
            entry: Entry XML element
            
        Returns:
            Article object or None if parsing fails
        """
        try:
            # Extract ID and remove the URL prefix
            id_elem = entry.find('atom:id', self.NAMESPACES)
            if id_elem is None:
                return None
            
            article_id = id_elem.text.replace('http://arxiv.org/abs/', '')
            
            # Extract title
            title_elem = entry.find('atom:title', self.NAMESPACES)
            title = title_elem.text.strip() if title_elem is not None else ""
            
            # Extract authors
            authors = self._parse_authors(entry)
            
            # Extract abstract
            summary_elem = entry.find('atom:summary', self.NAMESPACES)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""
            
            # Extract dates
            published_elem = entry.find('atom:published', self.NAMESPACES)
            published_date = self._parse_date(published_elem.text) if published_elem is not None else None
            
            updated_elem = entry.find('atom:updated', self.NAMESPACES)
            updated_date = self._parse_date(updated_elem.text) if updated_elem is not None else published_date
            
            # Extract categories
            categories = self._parse_categories(entry)
            
            # Extract primary category
            primary_cat_elem = entry.find('arxiv:primary_category', self.NAMESPACES)
            primary_category = primary_cat_elem.get('term') if primary_cat_elem is not None else None
            
            # Extract links (PDF, abstract page)
            links = self._parse_links(entry)
            
            # Extract arXiv-specific metadata
            comment_elem = entry.find('arxiv:comment', self.NAMESPACES)
            comment = comment_elem.text if comment_elem is not None else None
            
            journal_ref_elem = entry.find('arxiv:journal_ref', self.NAMESPACES)
            journal_ref = journal_ref_elem.text if journal_ref_elem is not None else None
            
            doi_elem = entry.find('arxiv:doi', self.NAMESPACES)
            doi = doi_elem.text if doi_elem is not None else None
            
            # Build metadata dictionary
            metadata = {
                'primary_category': primary_category,
                'categories': categories,
                'comment': comment,
                'journal_reference': journal_ref,
                'arxiv_id': article_id
            }
            
            # Create Article object
            article = Article(
                id=article_id,
                title=title,
                authors=authors,
                abstract=abstract,
                published_date=published_date,
                updated_date=updated_date,
                source=SourceType.ARXIV,
                url=links.get('abstract', f"http://arxiv.org/abs/{article_id}"),
                pdf_url=links.get('pdf'),
                doi=doi,
                categories=categories,
                metadata=metadata
            )
            
            return article
            
        except Exception as e:
            self._logger.warning(
                f"Failed to parse arXiv entry",
                error=str(e)
            )
            return None

    def _parse_authors(self, entry: ET.Element) -> List[Author]:
        """
        Parse author information from entry.
        
        Args:
            entry: Entry XML element
            
        Returns:
            List of Author objects
        """
        authors = []
        author_elements = entry.findall('atom:author', self.NAMESPACES)
        
        for author_elem in author_elements:
            name_elem = author_elem.find('atom:name', self.NAMESPACES)
            if name_elem is not None:
                name = name_elem.text.strip()
                
                # Check for affiliation
                affiliation_elem = author_elem.find('arxiv:affiliation', self.NAMESPACES)
                affiliation = affiliation_elem.text if affiliation_elem is not None else None
                
                authors.append(Author(
                    name=name,
                    affiliation=affiliation
                ))
        
        return authors

    def _parse_categories(self, entry: ET.Element) -> List[str]:
        """
        Parse category information from entry.
        
        Args:
            entry: Entry XML element
            
        Returns:
            List of category strings
        """
        categories = []
        category_elements = entry.findall('atom:category', self.NAMESPACES)
        
        for cat_elem in category_elements:
            term = cat_elem.get('term')
            if term:
                categories.append(term)
        
        return categories

    def _parse_links(self, entry: ET.Element) -> Dict[str, str]:
        """
        Parse link information from entry.
        
        Args:
            entry: Entry XML element
            
        Returns:
            Dictionary with link types as keys and URLs as values
        """
        links = {}
        link_elements = entry.findall('atom:link', self.NAMESPACES)
        
        for link_elem in link_elements:
            rel = link_elem.get('rel')
            title = link_elem.get('title')
            href = link_elem.get('href')
            
            if rel == 'alternate':
                links['abstract'] = href
            elif rel == 'related' and title == 'pdf':
                links['pdf'] = href
            elif rel == 'related' and title == 'doi':
                links['doi'] = href
        
        return links

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse ISO format date string to datetime object.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            datetime object or None if parsing fails
        """
        try:
            # ArXiv returns dates in ISO 8601 format
            # Example: 2003-07-07T13:46:39-04:00
            # Remove timezone info for simplicity
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
                time_part = date_str.split('T')[1].split('-')[0].split('+')[0]
                clean_date = f"{date_part}T{time_part}"
                return datetime.fromisoformat(clean_date)
            return datetime.fromisoformat(date_str)
        except Exception as e:
            self._logger.warning(f"Failed to parse date: {date_str}", error=str(e))
            return None

    async def get_articles_by_ids(self, article_ids: List[str]) -> List[Article]:
        """
        Retrieve multiple articles by their arXiv IDs.
        
        This method efficiently fetches multiple articles in a single API call.
        
        Args:
            article_ids: List of arXiv identifiers
            
        Returns:
            List of Article objects
            
        Raises:
            AdapterException: If the retrieval fails
        """
        try:
            await self._apply_rate_limit()
            
            # Clean article IDs
            clean_ids = [aid.split('v')[0] if 'v' in aid else aid for aid in article_ids]
            
            # Build URL with id_list parameter (comma-separated)
            url = self._build_url("query")
            params = {
                'id_list': ','.join(clean_ids),
                'max_results': len(clean_ids)
            }
            
            self._logger.info(
                f"Fetching multiple arXiv articles",
                count=len(clean_ids)
            )
            
            response = await self._http_client.get(url, params=params)
            
            # Parse response
            articles, _ = self._parse_atom_feed(response)
            
            self._logger.info(
                f"Retrieved multiple arXiv articles",
                requested=len(clean_ids),
                found=len(articles)
            )
            
            return articles
            
        except Exception as e:
            await self._handle_adapter_error(e, f"get_articles_by_ids")

    def validate_arxiv_id(self, article_id: str) -> bool:
        """
        Validate if a string is a valid arXiv identifier.
        
        ArXiv IDs can be in two formats:
        - Old: archive/YYMMNNN (e.g., hep-ex/0307015)
        - New: YYMM.NNNNN (e.g., 2301.12345)
        
        Args:
            article_id: String to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        
        # Old format: archive/YYMMNNN
        old_format = r'^[a-z\-]+/\d{7}(v\d+)?$'
        
        # New format: YYMM.NNNNN
        new_format = r'^\d{4}\.\d{4,5}(v\d+)?$'
        
        return bool(re.match(old_format, article_id) or re.match(new_format, article_id))