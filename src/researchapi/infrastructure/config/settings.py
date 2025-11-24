"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="ResearchAPI", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    app_environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Server
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=4, description="Number of workers")


class APIKeySettings(BaseSettings):
    """API keys for external services."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    springer_api_key: Optional[str] = Field(default=None, description="Springer API key")
    ieee_api_key: Optional[str] = Field(default=None, description="IEEE API key")


class RedisSettings(BaseSettings):
    """Redis cache configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    redis_enabled: bool = Field(default=True, description="Enable Redis cache")
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, description="Max cache size")

    @field_validator("redis_url", mode="before")
    @classmethod
    def build_redis_url(cls, v, info):
        """Build Redis URL if not provided."""
        if v:
            return v
        
        data = info.data
        host = data.get("redis_host", "localhost")
        port = data.get("redis_port", 6379)
        db = data.get("redis_db", 0)
        password = data.get("redis_password")
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Global rate limiting
    global_rate_limit_enabled: bool = Field(default=True)
    global_rate_limit_requests: int = Field(default=100)
    global_rate_limit_period: int = Field(default=60)
    
    # arXiv
    arxiv_rate_limit: int = Field(default=20)
    arxiv_rate_period: int = Field(default=60)
    arxiv_delay: int = Field(default=3)
    
    # Cambridge
    cambridge_rate_limit: int = Field(default=30)
    cambridge_rate_period: int = Field(default=60)
    cambridge_delay: int = Field(default=2)
    
    # IEEE
    ieee_rate_limit: int = Field(default=30)
    ieee_rate_period: int = Field(default=60)
    ieee_delay: int = Field(default=2)
    
    # Springer
    springer_rate_limit: int = Field(default=30)
    springer_rate_period: int = Field(default=60)
    springer_delay: int = Field(default=2)


class HTTPClientSettings(BaseSettings):
    """HTTP client configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    http_timeout: int = Field(default=30, description="Request timeout in seconds")
    http_max_retries: int = Field(default=3, description="Max retry attempts")
    http_retry_delay: int = Field(default=1, description="Initial retry delay")
    http_retry_backoff: int = Field(default=2, description="Retry backoff multiplier")
    http_connection_pool_size: int = Field(default=100)
    http_max_keepalive_connections: int = Field(default=20)


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    log_file_enabled: bool = Field(default=True)
    log_file_path: str = Field(default="logs/researchapi.log")
    log_file_max_size: int = Field(default=10485760)  # 10MB
    log_file_backup_count: int = Field(default=5)

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


class FeatureSettings(BaseSettings):
    """Feature flags configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Source toggles
    arxiv_enabled: bool = Field(default=True)
    cambridge_enabled: bool = Field(default=True)
    ieee_enabled: bool = Field(default=True)
    springer_enabled: bool = Field(default=True)
    
    # API features
    graphql_enabled: bool = Field(default=True)
    graphql_playground_enabled: bool = Field(default=True)
    graphql_introspection_enabled: bool = Field(default=True)
    
    # Monitoring
    health_check_enabled: bool = Field(default=True)
    metrics_enabled: bool = Field(default=True)


class SearchSettings(BaseSettings):
    """Default search parameters."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    default_max_results: int = Field(default=10)
    default_sort_by: str = Field(default="relevance")
    default_sort_order: str = Field(default="desc")


class SecuritySettings(BaseSettings):
    """Security configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # CORS
    cors_enabled: bool = Field(default=True)
    cors_origins: List[str] = Field(default=["*"])
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])
    
    # API Key Authentication
    api_key_enabled: bool = Field(default=False)
    api_key_header: str = Field(default="X-API-Key")
    api_keys: List[str] = Field(default_factory=list)


class Settings:
    """
    Main settings container.
    
    Aggregates all configuration sections.
    """
    
    def __init__(self):
        self.app = AppSettings()
        self.api_keys = APIKeySettings()
        self.redis = RedisSettings()
        self.rate_limit = RateLimitSettings()
        self.http_client = HTTPClientSettings()
        self.logging = LoggingSettings()
        self.features = FeatureSettings()
        self.search = SearchSettings()
        self.security = SecuritySettings()

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app.app_environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app.app_environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience function for getting settings
def load_settings() -> Settings:
    """Load and return settings."""
    return get_settings()
