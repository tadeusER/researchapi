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
    @classmethod
    def from_cambridge_response(cls, response_data: dict) -> "Article":
        article_data = response_data.get("data")
        if not article_data:
            return None

        # Extraer los campos necesarios de article_data
        article_id = article_data.get("id")
        title = article_data.get("title")
        authors = article_data.get("authors", [])
        summary = article_data.get("abstract", "")
        published_date = article_data.get("published_date")
        updated_date = article_data.get("updated_date")
        link = article_data.get("link")
        tags = article_data.get("tags", [])
        doi = article_data.get("doi", "not found")

        # Crear una instancia de Article con los datos extraídos
        article = cls(
            id=article_id,
            title=title,
            authors=authors,
            summary=summary,
            published_date=published_date,
            updated_date=updated_date,
            link=link,
            tags=tags,
            source="CambridgeAPI",  # Puedes establecer la fuente según sea necesario
            doi=doi
        )

        return article