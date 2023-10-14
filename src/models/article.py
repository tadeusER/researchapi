from typing import List
import strawberry

from models.response_arxiv import Entry
from models.response_cambrige import ItemHit
from models.response_springer import Chapter
from models.response_ieee import Article as ArticleIEEE
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
    def from_cambrige_response(cls, item_hit: ItemHit) -> "Article":
        authors_names = [f"{author.firstName} {author.lastName}" for author in item_hit.authors]
        keywords = item_hit.keywords
        published_date = item_hit.publishedDate.strftime('%Y-%m-%d')
        approved_date = item_hit.approvedDate.strftime('%Y-%m-%d')

        # Assuming the link to the article might be in the asset's URL (this might be different based on the actual data structure)
        link = item_hit.asset.original.url

        return cls(
            id=item_hit.item.get("id", ""),
            title=item_hit.item.get("title", ""),
            authors=authors_names,
            summary=item_hit.item.get("description", ""),
            published_date=published_date,
            updated_date=approved_date,  # This might be a different date, adjust as needed
            link=link,
            tags=keywords,
            source="Cambridge",
            doi=item_hit.item.get("doi", "not found")  # Adjust based on where the DOI might be
        )
    @classmethod
    def from_springer_chapter(cls, chapter: Chapter) -> "Article":
        authors_names = [creator.creator for creator in chapter.creators]
        published_date = chapter.publication_date
        # Asumiendo que la fecha de actualización no está disponible en los datos de Springer
        updated_date = published_date

        return cls(
            id=chapter.doi,
            title=chapter.title,
            authors=authors_names,
            summary=chapter.abstract,
            published_date=published_date,
            updated_date=updated_date,
            link=chapter.url[0].value if chapter.url else "",
            tags=chapter.subjects,
            source="Springer",
            doi=chapter.doi
        )
    @classmethod
    def from_ieee_article(cls, article: ArticleIEEE) -> "Article":
        # Asumiendo que la fecha de actualización no está disponible en los datos de IEEE
        updated_date = article.insert_date
        
        authors_names = [author.full_name for author in article.authors.authors]
        tags_ieee = article.index_terms.ieee_terms.terms
        tags_author = article.index_terms.author_terms.terms

        return cls(
            id=article.doi,
            title=article.title,
            authors=authors_names,
            summary=article.abstract,
            published_date=article.publication_date,
            updated_date=updated_date,
            link=article.pdf_url,
            tags=tags_ieee + tags_author,
            source="IEEE",
            doi=article.doi
        )
    