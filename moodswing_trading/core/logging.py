"""Logging configuration utilities."""

import logging
from logging.config import dictConfig

from .config import get_settings

settings = get_settings()

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": settings.log_level,
        "handlers": ["console"],
    },
}

def setup_logging() -> None:
    """Configure Python logging based on settings."""
    dictConfig(LOGGING_CONFIG)


__all__ = ["setup_logging"]