from typing import Dict, Any, Optional

from electric_text.tools.functions.load_tool_boxes import load_tool_boxes
from electric_text.tools.functions.validate_tool_box import validate_tool_box


def find_tool_box_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Find a tool box configuration by name.

    Args:
        name: Name of the tool box to find

    Returns:
        Dict[str, Any] or None: Tool box configuration if found, None otherwise
    """
    try:
        tool_boxes = load_tool_boxes()
        for tool_box in tool_boxes:
            if validate_tool_box(tool_box) and tool_box["name"] == name:
                return tool_box
    except (FileNotFoundError, ValueError):
        pass

    return None
