from typing import List
from adapters.arxiv_adapter import ArxivAPI
from adapters.base_adapter import BaseAdapter
from adapters.cambrige_adapter import CambridgeAPI
from api.fecade import SearchFacade
from models.article import Article

class ApiConsumer:
    adapters: List[BaseAdapter] = [
        ArxivAPI(),
        CambridgeAPI()
    ]
    def __init__(self) -> None:
        self.api_search = SearchFacade(self.adapters)
    def search_articles(self, query: str) -> List[Article]:
        return self.api_search.fetch_articles(query)
    def search_articles_from_queries(self, queries: List[str]) -> List[Article]:
        return self.api_search.fetch_articles_from_queries(queries)