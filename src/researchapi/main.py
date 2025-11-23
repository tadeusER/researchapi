"""
Main application entry point.

This module initializes the FastAPI application and all dependencies.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from infrastructure.config.settings import get_settings
from infrastructure.config.logging import setup_logging, get_logger, LoggerAdapter
from presentation.api.health import router as health_router
from presentation.api.search import router as search_router
from core.exceptions import ResearchAPIException


# Load settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.logging.log_level,
    log_format=settings.logging.log_format,
    log_file=settings.logging.log_file_path if settings.logging.log_file_enabled else None,
    log_file_max_size=settings.logging.log_file_max_size,
    log_file_backup_count=settings.logging.log_file_backup_count
)

# Get logger
logger = LoggerAdapter(get_logger(__name__))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting Research API",
        version=settings.app.app_version,
        environment=settings.app.app_environment
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
async def research_api_exception_handler(request, exc: ResearchAPIException):
    """Handle custom Research API exceptions."""
    logger.error(
        "Research API Exception",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.critical(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path
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
