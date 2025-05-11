import json
import os
from typing import List, Dict, Any

from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)


def load_tool_boxes() -> List[Dict[str, Any]]:
    """
    Load all tool box configurations from the tool_boxes.json file.

    Returns:
        List[Dict[str, Any]]: List of tool box configurations

    Raises:
        FileNotFoundError: If tool_boxes.json doesn't exist
        ValueError: If tool_boxes.json is invalid
    """
    config_dir = get_tool_configs_directory()
    tool_boxes_path = os.path.join(config_dir, "tool_boxes.json")

    if not os.path.exists(tool_boxes_path):
        raise FileNotFoundError(
            f"Tool boxes configuration not found: {tool_boxes_path}"
        )

    try:
        with open(tool_boxes_path, "r") as f:
            tool_boxes = json.load(f)

        if not isinstance(tool_boxes, list):
            raise ValueError("Tool boxes configuration must be a list")

        return tool_boxes
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid tool boxes configuration: {e}")
