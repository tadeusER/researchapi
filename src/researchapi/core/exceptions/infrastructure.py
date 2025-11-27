from typing import Optional, Dict, Any
from .base import ResearchAPIException


class AdapterException(ResearchAPIException):
    """Base exception for adapter-related errors."""
    pass


class AdapterConnectionError(AdapterException):
    """Raised when adapter cannot connect to external API."""
    pass


class AdapterTimeoutError(AdapterException):
    """Raised when adapter request times out."""
    pass


class AdapterRateLimitError(AdapterException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        if retry_after:
            self.details["retry_after"] = retry_after


class AdapterAuthenticationError(AdapterException):
    """Raised when authentication fails with external API."""
    pass


class AdapterResponseError(AdapterException):
    """Raised when external API returns an error response."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        if status_code:
            self.details["status_code"] = status_code


class AdapterParsingError(AdapterException):
    """Raised when response parsing fails."""
    pass


class ConfigurationException(ResearchAPIException):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationError(ConfigurationException):
    """Raised when required configuration is missing."""
    pass


class InvalidConfigurationError(ConfigurationException):
    """Raised when configuration is invalid."""
    pass