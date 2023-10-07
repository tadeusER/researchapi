from typing import List
from adapters.base_adapter import BaseAdapter
from models.article import Article
import requests

class SpringerAdapter(BaseAdapter):

    BASE_URL = "http://api.springernature.com/metadata/json"

    def __init__(self, api_key: str, default_results: int = 10):
        super().__init__(token=api_key)  # asumimos que el token es la api_key
        self.default_results = default_results
        self.base_params = {
                            'term': None,
                            'title': None,
                            'orgname': None,
                            'journal': None,
                            'book': None,
                            'name': None
                            }
        self.reset_parameters()
    def construct_query(self, **kwargs):
        query_parts = [f'{key}:"{value}"' for key, value in kwargs.items() if value and key in self.base_params]
        return ' AND '.join(query_parts)
    def search(self, query: str):
        params = {
            "q": query,
            "api_key": self.token,
            "p": self.default_results
        }

        response = requests.get(self.BASE_URL, params=params)
        # Suponemos que hay una función para convertir los registros en objetos Article
        return self.map_to_article(response.json().get('records', []))

    def get_article(self, article_id: str):
        # Suponiendo que la API de Springer permita la búsqueda por ID
        pass

    def multiple_search(self, queries: List[str]):
        all_results = []

        for query in queries:
            term_results = self.search(query)
            all_results.extend(term_results)

        return all_results

    def map_to_article(self, response_data) -> List[Article]:
        # Suponiendo que hay una función en la clase Article para crear una instancia desde un dict
        return [Article.from_dict(record) for record in response_data]

if __name__ == "__main__":
    YOUR_API_KEY = "yourKeyHere"
    adapter = SpringerAdapter(api_key=YOUR_API_KEY)
    
    # Ejemplo de búsqueda utilizando el nombre del autor y el título del artículo:
    search_results = adapter.search('name:"Salvador" AND title:"Quantum Computing"')
    
    for article in search_results:
        print(article)
