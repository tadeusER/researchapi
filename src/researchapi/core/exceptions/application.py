from typing import Optional, Dict, Any
from .base import ResearchAPIException



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
            
            
            
class FetchException(ResearchAPIException):
    """Raised when fetching data fails."""
    pass
