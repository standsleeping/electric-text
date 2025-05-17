import os
from typing import Optional


def get_tool_configs_directory() -> str:
    """
    Get the directory for tool configurations.

    Looks for USER_TOOL_CONFIGS_DIRECTORY environment variable.
    Falls back to the default examples/tool_configs directory if not set.

    Returns:
        str: Path to the tool configurations directory

    Raises:
        ValueError: If the tool configs directory doesn't exist
    """
    config_dir: Optional[str] = os.environ.get("USER_TOOL_CONFIGS_DIRECTORY")

    if not config_dir:
        raise ValueError("Tool configs directory is not set")

    return config_dir
