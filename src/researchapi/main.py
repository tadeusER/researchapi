"""
Main application entry point.

This module initializes the FastAPI application and all dependencies.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from researchapi.infrastructure.config.settings import get_settings
from researchapi.presentation.api.health import router as health_router
from researchapi.presentation.api.search import router as search_router
from researchapi.core.exceptions import ResearchAPIException

# Load settings
settings = get_settings()

# Get FastAPI logger
logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        f"Starting Research API - "
        f"version={settings.app.app_version}, "
        f"environment={settings.app.app_environment}"
    )
    
    # Initialize dependencies here
    # For example: database connections, cache, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down Research API")
    # Cleanup resources here


# Create FastAPI application
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="Academic Research Article Search API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# Configure CORS
if settings.security.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=settings.security.cors_allow_credentials,
        allow_methods=settings.security.cors_allow_methods,
        allow_headers=settings.security.cors_allow_headers,
    )


# Global exception handler
@app.exception_handler(ResearchAPIException)
async def research_api_exception_handler(request: Request, exc: ResearchAPIException):
    """Handle custom Research API exceptions."""
    logger.error(
        f"Research API Exception - "
        f"error_code={exc.error_code}, "
        f"message={exc.message}, "
        f"details={exc.details}, "
        f"path={request.url.path}"
    )
    
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.critical(
        f"Unhandled exception - "
        f"error={str(exc)}, "
        f"error_type={type(exc).__name__}, "
        f"path={request.url.path}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {} if settings.app.app_environment == "production" else {"error": str(exc)}
        }
    )


# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(search_router, prefix="/api/v1", tags=["Search"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app.app_name,
        "version": settings.app.app_version,
        "environment": settings.app.app_environment,
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.app.api_host,
        port=settings.app.api_port,
        reload=settings.app.debug,
        log_level=settings.logging.log_level.lower()
    )