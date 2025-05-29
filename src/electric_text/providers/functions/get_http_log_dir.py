import os
from pathlib import Path

from electric_text.configuration.functions.get_cached_config import get_cached_config


def get_http_log_dir() -> Path:
    """Get the HTTP log directory from config or environment variable.

    Priority order:
    1. ELECTRIC_TEXT_HTTP_LOG_DIR environment variable
    2. http_logging.log_dir in config file
    3. Default: "./http_logs"

    Returns:
        Path: Directory for HTTP logs
    """
    # Environment variable takes precedence
    env_value = os.getenv("ELECTRIC_TEXT_HTTP_LOG_DIR")
    if env_value is not None:
        return Path(env_value)

    # Fall back to config value
    try:
        config = get_cached_config()
        log_dir = config.http_logging.get("log_dir", "./http_logs")
        return Path(log_dir)
    except Exception:
        # If config loading fails, return default
        return Path("./http_logs")
