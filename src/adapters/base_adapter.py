from abc import ABC, abstractmethod

from utils.logger import get_logger

class BaseAdapter(ABC):

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def search(self, query: str):
        pass

    @abstractmethod
    def get_article(self, article_id: str):
        pass

