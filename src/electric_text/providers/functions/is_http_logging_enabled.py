import os

from electric_text.configuration.functions.get_cached_config import get_cached_config


def is_http_logging_enabled() -> bool:
    """Check if HTTP logging is enabled via config or environment variable.

    Priority order:
    1. ELECTRIC_TEXT_HTTP_LOGGING environment variable
    2. http_logging.enabled in config file
    3. Default: False

    Returns:
        bool: True if HTTP logging is enabled, False otherwise
    """
    # Environment variable takes precedence
    env_value = os.getenv("ELECTRIC_TEXT_HTTP_LOGGING")
    if env_value is not None:
        return env_value.lower() == "true"

    # Fall back to config value
    try:
        config = get_cached_config()
        return bool(config.http_logging.get("enabled", False))
    except Exception:
        # If config loading fails, return default
        return False
