"""Logging configuration for the package."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "electric_text", level: Optional[int] = None
) -> logging.Logger:
    """Set up and configure a logger.

    Args:
        name: The name of the logger
        level: The logging level (defaults to INFO)

    Returns:
        A configured logger instance
    """
    if level is None:
        level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if the logger already has handlers to avoid duplicates
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Create a default logger instance
logger = setup_logger()
