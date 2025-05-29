import os


def is_http_logging_enabled() -> bool:
    """Check if HTTP logging is enabled via environment variable.

    Returns:
        bool: True if ELECTRIC_TEXT_HTTP_LOGGING is set to "true", False otherwise
    """
    return os.getenv("ELECTRIC_TEXT_HTTP_LOGGING", "false").lower() == "true"
