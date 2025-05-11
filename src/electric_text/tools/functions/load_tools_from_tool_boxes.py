from typing import List, Dict, Any

from electric_text.tools.functions.load_tools_from_tool_box import (
    load_tools_from_tool_box,
)


def load_tools_from_tool_boxes(tool_box_names: List[str]) -> List[Dict[str, Any]]:
    """
    Load and combine tools from multiple tool boxes.

    Args:
        tool_box_names: List of tool box names to load tools from

    Returns:
        List[Dict[str, Any]]: Flat list of all tool configurations
    """
    all_tools: List[Dict[str, Any]] = []

    for tool_box_name in tool_box_names:
        try:
            tools = load_tools_from_tool_box(tool_box_name)
            all_tools.extend(tools)
        except ValueError:
            # Skip invalid tool boxes
            continue

    # Deduplicate tools by name
    unique_tools: Dict[str, Dict[str, Any]] = {}
    for tool in all_tools:
        if "name" in tool:
            unique_tools[tool["name"]] = tool

    return list(unique_tools.values())
