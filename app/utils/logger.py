"""
app/utils/logger.py

Centralised logging configuration for SmartFlow-Assistant.
All modules should import `logger` from here so log format and
level are consistent across the application.
"""

import logging
import sys


def _build_logger(name: str = "smartflow") -> logging.Logger:
    """Create and return a pre-configured logger."""
    log = logging.getLogger(name)

    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)

    log.setLevel(logging.INFO)
    return log


# Module-level logger instance used throughout the application.
logger: logging.Logger = _build_logger()
