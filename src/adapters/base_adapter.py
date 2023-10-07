from abc import ABC, abstractmethod
from logging import Logger
from typing import List
import urllib.request
import json
import time
from utils.logger import get_logger
from models.article import Article


class BaseAdapter(ABC):
    token: str
    base_params: dict
    logger: Logger
    def __init__(self, 
                 token: str = "", 
                 base_params: dict = None
                 ):
        self.logger = get_logger(self.__class__.__name__)
        self.token = token
        self.base_params = base_params or {}

    def reset_parameters(self):
        self.parameters = self.base_params.copy()
    
    def execute_search(self, url=None)-> dict:
        if not url:
            query_string = urllib.parse.urlencode(self.parameters)
            url = f"{self.BASE_URL}?{query_string}"
        self.logger.info(f"Request URL: {url}")
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
        )

        # Pasar el objeto Request a urlopen en lugar de la URL directamente
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        time.sleep(3)  # Espera 3 segundos antes de otra solicitud API
        return data
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