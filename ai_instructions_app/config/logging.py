"""Centralized logging configuration for the web application."""
from __future__ import annotations

import logging
from logging.config import dictConfig

from ai_instructions_app.config.settings import Settings


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}


def configure_logging(settings: Settings) -> None:
    """Configure logging for the application using the provided settings."""
    dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).debug(
        "Logging configured with settings: %s", settings.model_dump()
    )
