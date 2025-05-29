import os
from pathlib import Path


def get_http_log_dir() -> Path:
    """Get the HTTP log directory from environment variable.

    Returns:
        Path: Directory for HTTP logs, defaults to "./http_logs" if not set
    """
    log_dir = os.getenv("ELECTRIC_TEXT_HTTP_LOG_DIR", "./http_logs")
    return Path(log_dir)
