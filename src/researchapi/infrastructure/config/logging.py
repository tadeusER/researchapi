"""
Structured logging system using structlog.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    log_file_max_size: int = 10485760,
    log_file_backup_count: int = 5
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json or text)
        log_file: Optional log file path
        log_file_max_size: Max log file size in bytes
        log_file_backup_count: Number of backup files to keep
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Processors for structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer()
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup file logging if configured
    if log_file:
        setup_file_logging(
            log_file,
            log_level,
            log_format,
            log_file_max_size,
            log_file_backup_count
        )


def setup_file_logging(
    log_file: str,
    log_level: str,
    log_format: str,
    max_size: int,
    backup_count: int
) -> None:
    """
    Setup file-based logging with rotation.
    
    Args:
        log_file: Log file path
        log_level: Logging level
        log_format: Log format (json or text)
        max_size: Max file size before rotation
        backup_count: Number of backup files
    """
    from logging.handlers import RotatingFileHandler
    
    # Create log directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count
    )
    
    # Set formatter
    if log_format == "json":
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Add to root logger
    logging.root.addHandler(file_handler)


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LoggerAdapter:
    """
    Adapter to make structlog compatible with ILogger interface.
    """
    
    def __init__(self, logger: structlog.BoundLogger):
        self._logger = logger

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._logger.critical(message, **kwargs)
