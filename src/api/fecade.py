# api/facade.py
from models.article import Article
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def article(self, id: int) -> Article:
        # Here, you can use the repository pattern to get the article
        # I'm assuming you have a 'get_article_by_id' function for simplicity
        article_data = get_article_by_id(id)
        return Article(**article_data)
