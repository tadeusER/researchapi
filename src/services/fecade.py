from typing import List

from adapters.base_adapter import BaseAdapter
from models.article import Article

class SearchFacade:
    def __init__(self, adapters: List[BaseAdapter]):
        self.adapters = adapters

    def fetch_articles(self, query: str) -> List[Article]:
        articles = []
        for adapter in self.adapters:
            response = adapter.search(query)
            mapped_articles = adapter.map_to_article(response)
            articles.extend(mapped_articles)
        return articles

    def fetch_articles_from_queries(self, queries: List[str]) -> List[Article]:
        articles = []
        for adapter in self.adapters:
            responses = adapter.multiple_search(queries)
            mapped_articles = []
            for response in responses:
                mapped_articles.extend(adapter.map_to_article(response))
            articles.extend(mapped_articles)
        return articles
