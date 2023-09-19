from abc import ABC, abstractmethod
from typing import List

from utils.logger import get_logger
from models.article import Article


class BaseAdapter(ABC):

    def __init__(self, token: str = ""):
        self.logger = get_logger(self.__class__.__name__)
        self.token = token

    @abstractmethod
    def search(self, query: str):
        pass

    @abstractmethod
    def get_article(self, article_id: str):
        pass
    @abstractmethod
    def multiple_search(self, queries: List[str]):
        pass
    @abstractmethod
    def map_to_article(self, response_data) -> Article:
        """
        Convert the specific adapter response data into an Article instance.

        :param response_data: The raw data from the adapter's search or get_article method.
        :return: An Article instance.
        """
        pass