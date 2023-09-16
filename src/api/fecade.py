# api/facade.py
from adapters.arxiv_adapter import ArxivAPI
from models.article import Article
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def article(self, article_id: str) -> Article:
        arxiv_api = ArxivAPI()
        data = arxiv_api.get_article(article_id)
        return Article(id=data["id"], title=data["title"])

    @strawberry.field
    def articleByTitle(self, title: str) -> Article:
        arxiv_api = ArxivAPI()
        data = arxiv_api.search(title)  # Suponiendo que tu adaptador ArxivAPI tiene un método de búsqueda por título
        return Article(id=data["id"], title=data["title"])

