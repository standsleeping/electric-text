import os
from pathlib import Path


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
    config_dir = os.environ.get("USER_TOOL_CONFIGS_DIRECTORY")

    # Fall back to the default if not specified
    if not config_dir:
        # Get the root directory of the package
        root_dir = Path(__file__).parent.parent.parent.parent
        config_dir = str(root_dir / "examples" / "tool_configs")

    if not os.path.exists(config_dir):
        raise ValueError(f"Tool configs directory does not exist: {config_dir}")

    return config_dir
