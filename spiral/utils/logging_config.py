"""
Logging configuration for SpiralMind Nexus
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Setup logging configuration for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string, uses default if None
    """
    if format_string is None:
        format_string = "%(asctime)s %(levelname)s %(name)s :: %(message)s"
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels for better control
    logging.getLogger("spiral").setLevel(numeric_level)
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def configure_file_logging(filename: str, level: str = "DEBUG") -> None:
    """
    Add file logging handler
    
    Args:
        filename: Log file path
        level: Logging level for file handler
    """
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(getattr(logging, level.upper(), logging.DEBUG))
    
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s :: %(message)s"
    )
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    logging.getLogger().addHandler(file_handler)