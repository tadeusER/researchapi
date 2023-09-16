from abc import ABC, abstractmethod
from utils.logger import get_logger

class BaseSearchStrategy(ABC):
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def search(self, query: str):
        """Realiza una búsqueda basada en el query proporcionado."""
        pass

    def log_search(self, query: str):
        """Registra la búsqueda realizada."""
        self.logger.info(f"Executing search with query: {query}")