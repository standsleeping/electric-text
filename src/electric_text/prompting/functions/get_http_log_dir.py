import os

from electric_text.configuration.functions.get_cached_config import get_cached_config


def get_http_log_dir() -> str:
    """Get the HTTP log directory from config or environment variable."""
    # Environment variable takes precedence
    env_value = os.getenv("ELECTRIC_TEXT_HTTP_LOG_DIR")
    if env_value is not None:
        return env_value

    # Fall back to config value
    try:
        config = get_cached_config()
        log_dir = str(config.http_logging.get("log_dir", "./http_logs"))
        return log_dir
    except Exception:
        # If config loading fails, return default
        return "./http_logs"
