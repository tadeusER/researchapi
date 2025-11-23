"""
Core domain entities representing the business objects.

These are framework-independent and contain the core business logic.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class SourceType(str, Enum):
    """Enumeration of supported academic sources."""
    ARXIV = "arxiv"
    CAMBRIDGE = "cambridge"
    IEEE = "ieee"
    SPRINGER = "springer"


@dataclass
class Author:
    """Represents an article author."""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None

    def __str__(self) -> str:
        return self.name


@dataclass
class Article:
    """
    Core domain entity representing an academic article.
    
    This is the central domain model that all adapters map to.
    Framework-independent and contains only business logic.
    """
    
    # Required fields
    title: str
    source: SourceType
    
    # Identifiers
    id: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    
    # Content
    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    
    # Authors
    authors: List[Author] = field(default_factory=list)
    
    # Publication info
    publication_date: Optional[datetime] = None
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    publisher: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    
    # Categories and classification
    categories: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    
    # Metrics
    citation_count: Optional[int] = None
    
    # Metadata
    language: Optional[str] = None
    license: Optional[str] = None
    
    # Raw data from source (for debugging/auditing)
    raw_data: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure title is not empty
        if not self.title or not self.title.strip():
            raise ValueError("Article title cannot be empty")
        
        # Normalize title
        self.title = self.title.strip()
        
        # Extract year from date if not provided
        if self.publication_date and not self.publication_year:
            self.publication_year = self.publication_date.year

    @property
    def author_names(self) -> List[str]:
        """Get list of author names."""
        return [author.name for author in self.authors]

    @property
    def first_author(self) -> Optional[Author]:
        """Get the first author."""
        return self.authors[0] if self.authors else None

    @property
    def has_doi(self) -> bool:
        """Check if article has a DOI."""
        return bool(self.doi)

    @property
    def has_pdf(self) -> bool:
        """Check if article has a PDF link."""
        return bool(self.pdf_url)

    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source.value,
            "doi": self.doi,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "authors": [
                {
                    "name": author.name,
                    "affiliation": author.affiliation,
                    "email": author.email,
                    "orcid": author.orcid
                }
                for author in self.authors
            ],
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "publication_year": self.publication_year,
            "journal": self.journal,
            "publisher": self.publisher,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "categories": self.categories,
            "subjects": self.subjects,
            "citation_count": self.citation_count,
            "language": self.language,
            "license": self.license,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __str__(self) -> str:
        """String representation of the article."""
        authors_str = ", ".join(self.author_names[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        
        return f"{self.title} ({authors_str}, {self.publication_year or 'n.d.'})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Article(title='{self.title[:50]}...', source={self.source}, doi='{self.doi}')"


@dataclass
class SearchQuery:
    """Represents a search query with parameters."""
    
    query: str
    max_results: int = 10
    start_index: int = 0
    sort_by: str = "relevance"  # relevance, date, citations
    sort_order: str = "desc"  # asc, desc
    
    # Filters
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    authors: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    sources: List[SourceType] = field(default_factory=list)
    
    # Flags
    include_abstract: bool = True
    include_authors: bool = True

    def __post_init__(self):
        """Validate query parameters."""
        if not self.query or not self.query.strip():
            raise ValueError("Search query cannot be empty")
        
        if self.max_results < 1:
            raise ValueError("max_results must be at least 1")
        
        if self.start_index < 0:
            raise ValueError("start_index cannot be negative")


@dataclass
class SearchResult:
    """Represents the result of a search operation."""
    
    query: SearchQuery
    articles: List[Article]
    total_results: int
    source: SourceType
    execution_time: float  # in seconds
    
    # Pagination
    has_more: bool = False
    next_start_index: Optional[int] = None

    @property
    def count(self) -> int:
        """Number of articles in this result."""
        return len(self.articles)

    def __str__(self) -> str:
        return f"SearchResult(source={self.source}, count={self.count}, total={self.total_results})"
