from typing import Optional
from functools import lru_cache

from electric_text.configuration.data.config import Config
from electric_text.configuration.functions.load_config import load_config


@lru_cache(maxsize=1)
def get_cached_config(config_path: Optional[str] = None) -> Config:
    """Get the configuration with caching applied.

    Args:
        config_path: Optional path to the configuration file

    Returns:
        Cached Config instance
    """
    return load_config(config_path)