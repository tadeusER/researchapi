import json
import time
import urllib.request
from typing import List, Optional, Dict
from adapters.base_adapter import BaseAdapter
from models.article import Article


class CambridgeAPI(BaseAdapter):
    BASE_URL = 'https://www.cambridge.org/engage/miir/public-api/v1/items'  # Reemplazar con el dominio real de la API
    MAX_RESULTS = 50

    def __init__(self):
        super().__init__()
        self.parameters = {
            'term': "",
            'skip': 0,
            'limit': 10,
            'sort': "PUBLISHED_DATE_DESC"
        }

    def reset_parameters(self):
        self.parameters = {
            'term': "",
            'skip': 0,
            'limit': 10,
            'sort': "PUBLISHED_DATE_DESC"
        }

    def set_term(self, term: str):
        self.parameters['term'] = term
        return self

    # ... Aquí puedes agregar más métodos para establecer otros parámetros ...

    def execute_search(self, url=None):
        if not url:
            query_string = urllib.parse.urlencode(self.parameters)
            url = f"{self.BASE_URL}?{query_string}"
        self.logger.info(f"Request URL: {url}")
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        time.sleep(3)  # Espera 3 segundos antes de otra solicitud API
        return data

    def map_to_article(self, response_data) -> Article:
        article = Article.from_cambridge_response(response_data.get("data"))
        return article


    def search(self, query: str):
        self.set_term(query)
        response = self.execute_search()
        self.reset_parameters()
        return response

    def get_article_by_id(self, article_id: str):
        url = f"{self.BASE_URL}?itemId={article_id}"
        return self.execute_search(url)

    def get_article_by_doi(self, doi: str):
        url = f"{self.BASE_URL}/doi/{doi}"
        return self.execute_search(url)

    def multiple_search(self, queries: List[str]):
        responses = []

        for query in queries:
            cambridge_response = self.search(query)
            responses.append(cambridge_response)

        return responses


if __name__ == "__main__":
    api = CambridgeAPI()
    print(api.search("water flow"))
    print(api.get_article_by_id("123456"))  # Ejemplo de consulta por ID
    print(api.get_article_by_doi("10.33774/coe-2023-abcd"))  # Ejemplo de consulta por DOI
    queries = ["water", "flow", "physics"]
    print(api.multiple_search(queries))
