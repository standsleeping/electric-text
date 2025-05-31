import os
from pathlib import Path

from electric_text.configuration.functions.get_cached_config import get_cached_config


def get_prompt_directory() -> str:
    """Get the prompt directory from config or environment variable.

    Priority order:
    1. ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable
    2. prompts.directory in config file
    3. Raises ValueError if neither is set

    Returns:
        str: Directory path for prompts

    Raises:
        ValueError: If no prompt directory is configured
    """
    # Environment variable takes precedence
    env_value = os.getenv("ELECTRIC_TEXT_PROMPT_DIRECTORY")
    if env_value is not None:
        return env_value

    # Fall back to config value
    try:
        config = get_cached_config()
        directory = config.prompts.get("directory")
        if directory is not None:
            return directory
    except Exception:
        pass

    # If neither env var nor config is set, raise an error
    raise ValueError("ELECTRIC_TEXT_PROMPT_DIRECTORY environment variable is not set and prompts.directory is not configured")