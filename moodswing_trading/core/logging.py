"""Logging configuration utilities."""

import logging
import json
from logging.config import dictConfig

from .config import get_settings

settings = get_settings()

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        return json.dumps(payload)


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "core.logging.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
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