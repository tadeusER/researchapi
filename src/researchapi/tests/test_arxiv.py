import pytest
import feedparser

from adapters.arxiv_adapter import ArxivAPI
from models.response_arxiv import ArxivResponse

# Crear una instancia de ArxivAPI para las pruebas
api = ArxivAPI()

def read_sample_response():
    """Lee un XML de muestra desde un archivo y lo devuelve."""
    with open("./src/testdata/sample_response_arxiv.xml", "r") as file:
        return file.read()

@pytest.fixture
def sample_feed():
    """Un fixture de pytest que devuelve el feed parseado de la respuesta de muestra."""
    sample_response = read_sample_response()
    return feedparser.parse(sample_response)

def test_parse_response(sample_feed):
    """Prueba la función _parse_response."""
    result = api._parse_response(sample_feed)
    
    # Asegúrate de que el resultado es una instancia de ArxivResponse
    assert isinstance(result, ArxivResponse)
    
    # Aquí puedes añadir más aserciones basadas en lo que esperas del XML de muestra
    # Por ejemplo:
    assert len(result.entries) > 0
    assert result.bozo is False
    # ... y así sucesivamente para los otros campos ...

def test_search(monkeypatch, sample_feed):
    """Prueba la función search."""

    # Mockear la función execute_search para que devuelva el feed de muestra en lugar de hacer una solicitud real
    def mock_execute_search(*args, **kwargs):
        return sample_feed
    
    monkeypatch.setattr(api, "execute_search", mock_execute_search)

    result = api.search("test query")

    # Asegúrate de que el resultado es una instancia de ArxivResponse
    assert isinstance(result, ArxivResponse)
