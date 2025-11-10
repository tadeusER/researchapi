

from config.base_config import BaseConfig

def test_base_config_defaults():
    config = BaseConfig()
    assert config.get_database_url() == "sqlite:///./test.db"
    assert config.get_log_level() == "DEBUG"