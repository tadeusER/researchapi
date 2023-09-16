import pytest
from adapters.arxiv_adapter import ArxivAPI
import requests_mock
from adapters.base_adapter import BaseAdapter

# Los siguientes son endpoints de ejemplo que mockearemos.
mock_search_url = "http://export.arxiv.org/api/query?start=0&max_results=10&search_query=all%3ASample"
mock_search_response = """
<feed>
  <entry>
    <id>http://arxiv.org/abs/123</id>
    <title>Sample Article</title>
  </entry>
</feed>
"""

mock_get_article_url = "http://export.arxiv.org/api/query?id_list=123&start=0&max_results=10"
mock_get_article_response = """
<feed>
  <entry>
    <id>http://arxiv.org/abs/123</id>
    <title>Sample Article</title>
  </entry>
</feed>
"""

@pytest.mark.parametrize("url, response, expected_result", [
    (mock_search_url, mock_search_response, [{"id": "123", "title": "Sample Article"}]),
    (mock_get_article_url, mock_get_article_response, {"id": "123", "title": "Sample Article"})
])
def test_arxiv_api(url, response, expected_result):
    with requests_mock.Mocker() as m:
        m.get(url, text=response)

        api = ArxivAPI()

        if "search_query" in url:
            result = api.search("Sample")
        else:
            result = api.get_article("123")

        assert result == expected_result
