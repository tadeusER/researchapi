import pytest
from adapters.base_adapter import BaseAdapter

# Aquí creamos un MockAdapter para las pruebas, que hereda de BaseAdapter
class MockAdapter(BaseAdapter):
    def search(self, query: str):
        return [{"id": "123", "title": "Sample Article"}]

    def get_article(self, article_id: str):
        return {"id": "123", "title": "Sample Article"}
    
    # Añadimos las implementaciones ficticias de los métodos abstractos
    def map_to_article(self, data):
        return {"id": data["id"], "title": data["title"]}

    def multiple_search(self, queries):
        return [{"id": "123", "title": "Sample Article for query {}".format(query)} for query in queries]

# Ahora, escribimos las pruebas para el adaptador

def test_adapter_search():
    adapter = MockAdapter()
    results = adapter.search("Sample")
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert "id" in results[0]
    assert "title" in results[0]

def test_adapter_get_article():
    adapter = MockAdapter()
    article = adapter.get_article("123")
    
    assert isinstance(article, dict)
    assert "id" in article
    assert "title" in article

def test_adapter_map_to_article():
    adapter = MockAdapter()
    mapped_article = adapter.map_to_article({"id": "123", "title": "Sample Article"})
    
    assert isinstance(mapped_article, dict)
    assert "id" in mapped_article
    assert "title" in mapped_article

def test_adapter_multiple_search():
    adapter = MockAdapter()
    results = adapter.multiple_search(["Sample1", "Sample2"])
    
    assert isinstance(results, list)
    assert len(results) == 2
    for result in results:
        assert "id" in result
        assert "title" in result

