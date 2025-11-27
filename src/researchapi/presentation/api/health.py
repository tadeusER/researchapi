"""
Health check endpoints for monitoring.
"""

from typing import Dict, Any
from datetime import datetime
from datetime import timezone
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from researchapi.infrastructure.config.settings import get_settings


router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    services: Dict[str, Any]


class ServiceHealth(BaseModel):
    """Individual service health status."""
    available: bool
    message: str
    latency_ms: float = 0.0


@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        HealthStatus with basic application information
    """
    settings = get_settings()
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.app.app_version,
        environment=settings.app.app_environment,
        services={}
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes.
    
    Returns:
        200 if application is ready to serve traffic
    """
    settings = get_settings()
    
    # Check if critical services are available
    services_ready = {
        "api": True,
        # Add checks for other services here
        # "redis": await check_redis(),
        # "adapters": await check_adapters()
    }
    
    all_ready = all(services_ready.values())
    
    return {
        "ready": all_ready,
        "services": services_ready,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes.
    
    Returns:
        200 if application is alive
    """
    return {
        "alive": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with all service statuses.
    
    Returns:
        Detailed health information for all services
    """
    settings = get_settings()
    
    # Check each source adapter
    adapters_health = {
        "arxiv": {
            "enabled": settings.features.arxiv_enabled,
            "status": "healthy" if settings.features.arxiv_enabled else "disabled"
        },
        "cambridge": {
            "enabled": settings.features.cambridge_enabled,
            "status": "healthy" if settings.features.cambridge_enabled else "disabled"
        },
        "ieee": {
            "enabled": settings.features.ieee_enabled,
            "status": "healthy" if settings.features.ieee_enabled else "disabled",
            "configured": settings.api_keys.ieee_api_key is not None
        },
        "springer": {
            "enabled": settings.features.springer_enabled,
            "status": "healthy" if settings.features.springer_enabled else "disabled",
            "configured": settings.api_keys.springer_api_key is not None
        }
    }
    
    # Cache health
    cache_health = {
        "enabled": settings.redis.redis_enabled,
        "type": "redis" if settings.redis.redis_enabled else "memory",
        "status": "unknown"  # Would check actual connection here
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.app.app_version,
        "environment": settings.app.app_environment,
        "services": {
            "adapters": adapters_health,
            "cache": cache_health
        }
    }
