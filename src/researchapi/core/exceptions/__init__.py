"""
Custom exceptions for the Research API domain.

These exceptions represent domain-specific errors and are framework-independent.
"""
from typing import Optional, Dict, Any
from .base import ResearchAPIException
from .application import *
from .infrastructure import *
from .presentation import * 


class CacheException(ResearchAPIException):
    """Base exception for cache-related errors."""
    pass


class CacheConnectionError(CacheException):
    """Raised when cannot connect to cache."""
    pass


class CacheOperationError(CacheException):
    """Raised when cache operation fails."""
    pass
