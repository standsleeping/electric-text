from typing import Any


def validate_tool_box(tool_box: Any) -> bool:
    """
    Validate a tool box configuration.

    Args:
        tool_box: Tool box configuration to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(tool_box, dict):
        return False

    required_fields = ["name", "tools"]
    for field in required_fields:
        if field not in tool_box:
            return False

    if not isinstance(tool_box["tools"], list):
        return False

    return True
