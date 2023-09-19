import json
import time
import urllib.request
from typing import List, Optional, Dict

from marshmallow import ValidationError
from adapters.base_adapter import BaseAdapter
from models.article import Article
from models.response_cambrige import CambrigeResponse, CambrigeResponseSchema


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

    def execute_search(self, url=None)-> dict:
        if not url:
            query_string = urllib.parse.urlencode(self.parameters)
            url = f"{self.BASE_URL}?{query_string}"
        self.logger.info(f"Request URL: {url}")
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        time.sleep(3)  # Espera 3 segundos antes de otra solicitud API
        return data

    def map_to_article(self, response_data: CambrigeResponse) -> List[Article]:
        articles = []

        if not response_data or not response_data.itemHits:
            self.logger.warning("The provided CambrigeResponse object is empty or has no itemHits.")
            return articles

        for item_hit in response_data.itemHits:
            try:
                article = Article.from_cambrige_response(item_hit)
                articles.append(article)
            except Exception as e:
                # Log the exception and continue processing the remaining items
                self.logger.error(f"Error mapping ItemHit (ID: {item_hit.item.get('id', 'Unknown')}) to Article: {str(e)}")

        self.logger.info(f"Successfully mapped {len(articles)} out of {len(response_data.itemHits)} ItemHits to Articles.")

        return articles


    def search(self, query: str) -> CambrigeResponse:
        self.set_term(query)
        response_data = self.execute_search()
        self.reset_parameters()

        # Usar el esquema para cargar la respuesta en un objeto CambrigeResponse
        schema = CambrigeResponseSchema()
        try:
            cambrige_response = schema.load(response_data)
            self.logger.info(f"type cambrige_response: {type(cambrige_response)}")
            return cambrige_response
        except ValidationError as e:
            self.logger.error(f"Error deserializando la respuesta: {e.messages}")
            # Puedes manejar el error como prefieras, por ejemplo:
            raise ValueError("Error procesando la respuesta de la API.")

    def get_article_by_id(self, article_id: str) -> CambrigeResponse:
        url = f"{self.BASE_URL}?itemId={article_id}"
        response_data = self.execute_search(url)

        schema = CambrigeResponseSchema()
        try:
            cambrige_response = schema.load(response_data)
            return cambrige_response
        except ValidationError as e:
            self.logger.error(f"Error deserializando la respuesta: {e.messages}")
            raise ValueError("Error procesando la respuesta de la API.")

    def get_article_by_doi(self, doi: str) -> CambrigeResponse:
        url = f"{self.BASE_URL}/doi/{doi}"
        response_data = self.execute_search(url)

        schema = CambrigeResponseSchema()
        try:
            cambrige_response = schema.load(response_data)
            return cambrige_response
        except ValidationError as e:
            self.logger.error(f"Error deserializando la respuesta: {e.messages}")
            raise ValueError("Error procesando la respuesta de la API.")
    def get_article(self, article_id: str):
        pass
    def multiple_search(self, queries: List[str]) -> List[CambrigeResponse]:
        responses = []
            
        for query in queries:
            try:
                cambridge_response = self.search(query)
                responses.append(cambridge_response)
                self.logger.info(f"Consulta exitosa para: {query}")
            except Exception as e:  # Puede ser más específico con el tipo de excepción según sea necesario.
                self.logger.error(f"Error al buscar la consulta '{query}': {e}")
            
        return responses


if __name__ == "__main__":
    api = CambridgeAPI()
    print(api.search("water flow"))
    print(api.get_article_by_id("123456"))  # Ejemplo de consulta por ID
    print(api.get_article_by_doi("10.33774/coe-2023-abcd"))  # Ejemplo de consulta por DOI
    queries = ["water", "flow", "physics"]
    print(api.multiple_search(queries))
