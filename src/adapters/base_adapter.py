from abc import ABC, abstractmethod

class BaseAdapter(ABC):

    @abstractmethod
    def search(self, query: str):
        """
        Realiza una búsqueda basada en la consulta proporcionada y devuelve los resultados.

        Args:
            query (str): La consulta de búsqueda.

        Returns:
            list: Una lista de resultados.
        """
        pass
    
    @abstractmethod
    def get_article(self, article_id: str):
        """
        Obtiene un artículo específico basado en su ID.

        Args:
            article_id (str): El ID del artículo.

        Returns:
            dict: Información del artículo.
        """
        pass
