import os


def get_log_level() -> str:
    """Get the log level from environment variable.
    
    Returns:
        str: Log level from ELECTRIC_TEXT_LOG_LEVEL, defaults to "INFO" if not set
    """
    return os.getenv("ELECTRIC_TEXT_LOG_LEVEL", "INFO")