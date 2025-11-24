"""
Custom exceptions for the Research API domain.

These exceptions represent domain-specific errors and are framework-independent.
"""

from typing import Optional, Dict, Any


class ResearchAPIException(Exception):
    """Base exception for all Research API errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


# ==========================================
# Adapter Exceptions
# ==========================================

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


# ==========================================
# Validation Exceptions
# ==========================================

class ValidationException(ResearchAPIException):
    """Base exception for validation errors."""
    pass


class InvalidQueryError(ValidationException):
    """Raised when search query is invalid."""
    pass


class InvalidParameterError(ValidationException):
    """Raised when parameter validation fails."""
    pass


class MissingRequiredFieldError(ValidationException):
    """Raised when required field is missing."""
    pass


# ==========================================
# Business Logic Exceptions
# ==========================================

class BusinessLogicException(ResearchAPIException):
    """Base exception for business logic errors."""
    pass


class ArticleNotFoundError(BusinessLogicException):
    """Raised when article is not found."""
    pass


class SearchFailedError(BusinessLogicException):
    """Raised when search operation fails."""
    pass


class TooManyResultsError(BusinessLogicException):
    """Raised when search returns too many results."""
    
    def __init__(
        self,
        message: str,
        max_results: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if max_results:
            self.details["max_results"] = max_results


# ==========================================
# Cache Exceptions
# ==========================================

class CacheException(ResearchAPIException):
    """Base exception for cache-related errors."""
    pass


class CacheConnectionError(CacheException):
    """Raised when cannot connect to cache."""
    pass


class CacheOperationError(CacheException):
    """Raised when cache operation fails."""
    pass


# ==========================================
# Configuration Exceptions
# ==========================================

class ConfigurationException(ResearchAPIException):
    """Base exception for configuration errors."""
    pass


class MissingConfigurationError(ConfigurationException):
    """Raised when required configuration is missing."""
    pass


class InvalidConfigurationError(ConfigurationException):
    """Raised when configuration is invalid."""
    pass


# ==========================================
# Service Exceptions
# ==========================================

class ServiceException(ResearchAPIException):
    """Base exception for service-layer errors."""
    pass


class ServiceUnavailableError(ServiceException):
    """Raised when a service is unavailable."""
    pass


class MultipleSourcesFailedError(ServiceException):
    """Raised when multiple sources fail."""
    
    def __init__(
        self,
        message: str,
        failed_sources: Optional[list] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        if failed_sources:
            self.details["failed_sources"] = failed_sources
