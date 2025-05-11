import json
import os
from typing import Dict, Any, Optional

from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)


def load_tool_config(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a single tool configuration by name.

    Args:
        tool_name: Name of the tool to load

    Returns:
        Dict[str, Any] or None: Tool configuration if found, None otherwise
    """
    config_dir = get_tool_configs_directory()
    tool_path = os.path.join(config_dir, f"{tool_name}.json")

    if not os.path.exists(tool_path):
        return None

    try:
        with open(tool_path, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return None
    except (json.JSONDecodeError, IOError):
        return None
