from typing import List

from marshmallow import ValidationError
from adapters.base_adapter import BaseAdapter
from models.article import Article
from models.response_springer import SpringerResponse, SpringerResponseSchema

class SpringerAdapter(BaseAdapter):

    BASE_URL = "http://api.springernature.com/metadata/json"

    def __init__(self, api_key: str, default_results: int = 10):
        super().__init__(token=api_key)  # asumimos que el token es la api_key
        self.default_results = default_results
        self.base_query = {
                            'term': None,
                            'title': None,
                            'orgname': None,
                            'journal': None,
                            'book': None,
                            'name': None
                            }
        self.base_params = {
            "q": None,
            "api_key": self.token,
            "p": self.default_results
        }
        self.reset_parameters()
    def list_params_query(self):
        return list(self.base_query.keys())
    def construct_query(self, **kwargs):
        self.logger.info(f"transform kwargs: {kwargs}")
        query_parts = []
        
        for key, value in kwargs.items():
            if key in self.base_query:  # Solo añadir a la consulta si el valor no es None o una cadena vacía, y la clave está en self.base_query
                if key == 'term':
                    query_parts.append(f'"{value}"')  # Solo incluye el valor si la clave es 'term'
                else:
                    query_parts.append(f'{key}:"{value}"')  # Incluye la clave y el valor para otras claves

        return ' AND '.join(query_parts)

    def map_to_article(self, response_data: SpringerResponse) -> List[Article]:
        articles = []

        if not response_data or not response_data.chapters:
            self.logger.warning("The provided SpringerResponse object is empty or has no chapters.")
            return articles

        for chapter in response_data.chapters:
            try:
                article = Article.from_springer_chapter(chapter)
                articles.append(article)
            except Exception as e:
                # Log the exception and continue processing the remaining items
                self.logger.error(f"Error mapping Chapter (DOI: {chapter.doi}) to Article: {str(e)}")

        self.logger.info(f"Successfully mapped {len(articles)} out of {len(response_data.chapters)} Chapters to Articles.")

        return articles
    def search(self, query=None, **kwargs):
        if query:
            kwargs['term'] = query
        constructed_query = self.construct_query(**kwargs)
        self.parameters['q'] = constructed_query
        response_data = self.execute_search()
        self.reset_parameters()
        response_data = response_data['records']
        # Usar el esquema para cargar la respuesta en un objeto CambrigeResponse
        schema = SpringerResponseSchema()
        try:
            cambrige_response = schema.load({"chapters": response_data})
            self.logger.info(f"type cambrige_response: {type(cambrige_response)}")
            return cambrige_response
        except ValidationError as e:
            self.logger.error(f"Error deserializando la respuesta: {e.messages}")
            # Puedes manejar el error como prefieras, por ejemplo:
            raise ValueError("Error procesando la respuesta de la API.")

    def get_article(self, article_id: str):
        # Suponiendo que la API de Springer permita la búsqueda por ID
        pass

    def multiple_search(self, queries: List[str])->List[SpringerResponse]:
        all_results = []

        for query in queries:
            term_results = self.search(term=query)
            all_results.extend(term_results)

        return all_results

if __name__ == "__main__":
    YOUR_API_KEY = "yourKeyHere"
    adapter = SpringerAdapter(api_key=YOUR_API_KEY)
    
    # Ejemplo de búsqueda utilizando el nombre del autor y el título del artículo:
    search_results = adapter.search('name:"Salvador" AND title:"Quantum Computing"')
    
    for article in search_results:
        print(article)
