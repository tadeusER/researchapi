
import urllib.parse
import time
from adapters.base_adapter import BaseAdapter
import feedparser

from models.response_arxiv import ArxivResponse

class ArxivAPI(BaseAdapter):
    BASE_URL = 'http://export.arxiv.org/api/query'
    MAX_RESULTS_SLICE = 2000

    def __init__(self):
        super().__init__()
        self.parameters = {
            'start': 0,
            'max_results': 10
        }

    def add_field_search(self, field, term):
        term = urllib.parse.quote(term)
        if 'search_query' in self.parameters:
            self.parameters['search_query'] += f'+AND+{field}:{term}'
        else:
            self.parameters['search_query'] = f"{field}:{term}"
        return self

    def set_id_list(self, id_list):
        self.parameters['id_list'] = ','.join(id_list)
        return self

    def set_start(self, start):
        self.parameters['start'] = start
        return self

    def set_max_results(self, max_results):
        self.parameters['max_results'] = min(max_results, self.MAX_RESULTS_SLICE)
        return self

    def set_sort_by(self, sort_by):
        if sort_by in ["relevance", "lastUpdatedDate", "submittedDate"]:
            self.parameters['sortBy'] = sort_by
        return self

    def set_sort_order(self, order):
        if order in ["ascending", "descending"]:
            self.parameters['sortOrder'] = order
        return self

    def execute_search(self, method="GET"):
        if method.upper() == "GET":
            # Convertir los parámetros a cadena de consulta
            query_string = urllib.parse.urlencode(self.parameters)
            full_url = f"{self.BASE_URL}?{query_string}"
            self.logger.info(f"Request URL: {full_url}")
            response = urllib.request.urlopen(full_url)
        else: # POST request
            # Aquí asumiré que los parámetros son enviados como un formulario codificado en formato x-www-form-urlencoded
            data_encoded = urllib.parse.urlencode(self.parameters).encode('utf-8')
            response = urllib.request.urlopen(self.BASE_URL, data=data_encoded)

        feed = feedparser.parse(response.read().decode('utf-8'))
        time.sleep(3)  # Wait for 3 seconds before another API request to be kind to the server
        return feed
    def _parse_response(self, response: dict):
        res = ArxivResponse.from_dict(response)
        return res
    
    def search(self, query: str):
        """Perform a single search with the provided query."""
        self.logger.debug(f"Starting search with query: {query}")
        self.add_field_search("all", query)
        response = self.execute_search()
        self.logger.debug(f"Finished search for query: {query}")
        return self._parse_response(response)

    def get_article(self, article_id: str):
        """Obtiene un artículo específico basado en su ID."""
        self.logger.debug(f"Fetching article with ID: {article_id}")
        self.set_id_list([article_id])
        response = self.execute_search()
        self.logger.debug(f"Retrieved article with ID: {article_id}")
        articles_response = self._parse_response(response)
        return articles_response.entries[0] if articles_response.entries else None
    def multiple_search(self, query: str, total_results: int):
        """Realiza múltiples búsquedas hasta obtener el número total deseado de resultados."""
        articles = []
        current_start = 0
        while len(articles) < total_results:
            self.set_start(current_start)
            response = self.execute_search()
            articles.extend(self._parse_response(response))
            current_start += self.parameters['max_results']

            if len(articles) >= total_results:
                return articles[:total_results]  # return only the desired number of articles

            if len(self._parse_response(response)) == 0:  # stop if there are no more results
                break

        return articles
    
if __name__=="__main__":
    api = ArxivAPI()
    print(api.search("electron thermal conductivity"))  # Realiza una búsqueda única
    print(api.multiple_search("electron", 5000))  # Realiza múltiples búsquedas hasta obtener 5000 resultados

