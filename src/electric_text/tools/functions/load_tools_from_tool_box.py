from typing import List, Dict, Any

from electric_text.tools.functions.find_tool_box_by_name import find_tool_box_by_name
from electric_text.tools.functions.load_tool_config import load_tool_config
from electric_text.tools.functions.validate_tool_box import validate_tool_box


def load_tools_from_tool_box(tool_box_name: str) -> List[Dict[str, Any]]:
    """
    Load all tool configurations from a specific tool box.

    Args:
        tool_box_name: Name of the tool box to load tools from

    Returns:
        List[Dict[str, Any]]: List of tool configurations

    Raises:
        ValueError: If the tool box doesn't exist or is invalid
    """
    tool_box = find_tool_box_by_name(tool_box_name)

    if not tool_box:
        raise ValueError(f"Tool box not found: {tool_box_name}")

    if not validate_tool_box(tool_box):
        raise ValueError(f"Invalid tool box configuration: {tool_box_name}")

    tools: List[Dict[str, Any]] = []
    for tool_name in tool_box["tools"]:
        tool_config = load_tool_config(tool_name)
        if tool_config:
            tools.append(tool_config)

    return tools
