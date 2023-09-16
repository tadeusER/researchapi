import pytest
from adapters.base_adapter import BaseAdapter

# Aquí creamos un MockAdapter para las pruebas, que hereda de BaseAdapter
class MockAdapter(BaseAdapter):
    def search(self, query: str):
        return [{"id": "123", "title": "Sample Article"}]

    def get_article(self, article_id: str):
        return {"id": "123", "title": "Sample Article"}

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