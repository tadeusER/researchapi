import json
import pytest
from adapters.cambrige_adapter import CambridgeAPI
from models.response_cambrige import CambrigeResponse, ItemHit

@pytest.fixture
def sample_response():
    with open("./src/testdata/sample_response_cambrige.json", "r") as file:
        data = json.load(file)
        return data

def test_search(monkeypatch, sample_response):
    def mock_execute_search(*args, **kwargs):
        return sample_response

    monkeypatch.setattr(CambridgeAPI, "execute_search", mock_execute_search)
    api = CambridgeAPI()
    response = api.search("test_query")

    assert isinstance(response, CambrigeResponse), f"Expected CambrigeResponse but got {type(response)}"
    assert response.totalCount == sample_response["totalCount"], f"Expected {sample_response['totalCount']} but got {response.totalCount}"
    
    # Verificando si el primer ItemHit coincide con el contenido del archivo JSON
    first_item_hit = response.itemHits[0]
    assert isinstance(first_item_hit, ItemHit), f"Expected ItemHit but got {type(first_item_hit)}"