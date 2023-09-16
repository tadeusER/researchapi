import requests
import urllib.parse
import time
import xml.etree.ElementTree as ET
from adapters.base_adapter import BaseAdapter

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
            response = requests.get(self.BASE_URL, params=self.parameters)
        else: # POST request
            response = requests.post(self.BASE_URL, data=self.parameters)
        self.logger.info(f"Request URL: {response.url}")
        time.sleep(3)  # Wait for 3 seconds before another API request to be kind to the server
        return response.text

    def _parse_response(self, xml_content):
        root = ET.fromstring(xml_content)
        articles = []
        for entry in root.findall('.//entry'):
            id_elem = entry.find('id')
            title_elem = entry.find('title')
            
            article = {}
            if id_elem is not None:
                # Extract the real ID from the URL
                article['id'] = id_elem.text.split('/')[-1]
            if title_elem is not None:
                article['title'] = title_elem.text
            
            articles.append(article)
        
        return articles

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
        articles = self._parse_response(response)
        return articles[0] if articles else None






if __name__=="__main__":
    api = ArxivAPI()
    print(api.search("electron thermal conductivity"))  # Realiza una búsqueda única
    print(api.multiple_search("electron", 5000))  # Realiza múltiples búsquedas hasta obtener 5000 resultados

