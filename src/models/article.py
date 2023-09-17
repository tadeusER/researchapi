from typing import List
import strawberry

from models.response_arxiv import Entry

@strawberry.type
class Article:
    id: str
    title: str
    authors: List[str]
    summary: str
    published_date: str
    updated_date: str
    link: str
    tags: List[str]
    source: str
    doi: str
    @classmethod
    def from_arxiv_entry(cls, entry: Entry) -> "Article":
        return cls(
            id=entry.id,
            title=entry.title,
            authors=[author.name for author in entry.authors],
            summary=entry.summary,
            published_date=entry.published,
            updated_date=entry.updated,
            link=entry.link,
            tags=[tag.term for tag in entry.tags],
            source="Arxiv",
            doi=getattr(entry, 'arxiv_doi', "not found")
        )