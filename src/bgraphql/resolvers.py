
from typing import List
import strawberry
from models.article import Article
from api.api_consumer import ApiConsumer
_api_consumer = ApiConsumer()
@strawberry.type
class Query:

    @strawberry.field
    def article(self, article_id: str) -> Article:
        articles = _api_consumer.search_articles(article_id)
        return articles[0] if articles else None  # Devuelve el primer artículo si hay alguno, de lo contrario None.

    @strawberry.field
    def articlesByTitle(self, title: str) -> List[Article]:
        return _api_consumer.search_articles(title)
    @strawberry.field
    def articlesByTitles(self, titles: List[str]) -> List[Article]:
        return _api_consumer.search_articles_from_queries(titles)
