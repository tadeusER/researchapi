# src/config/base_config.py

import os

class BaseConfig:
    """Configuración base del proyecto."""
    
    def __init__(self):
        self.DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
        self.LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

    def get_database_url(self):
        return self.DATABASE_URL

    def get_log_level(self):
        return self.LOG_LEVEL
