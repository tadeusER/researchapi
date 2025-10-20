import pytest
from search_strategies.base_search_strategy import BaseSearchStrategy

def test_base_search_strategy_initialization():
    with pytest.raises(TypeError):
        strategy = BaseSearchStrategy()