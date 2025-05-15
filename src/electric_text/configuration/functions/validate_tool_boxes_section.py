from typing import Dict, Any, List


def validate_tool_boxes_section(tool_boxes: Dict[str, Any]) -> List[str]:
    """Validate the tool_boxes section of the configuration.

    Args:
        tool_boxes: The tool_boxes configuration to validate

    Returns:
        List of validation issues
    """
    issues: List[str] = []

    for box_name, tools in tool_boxes.items():
        if not isinstance(tools, list):
            issues.append(
                f"Invalid tools list for tool box {box_name}. Must be a list."
            )

    return issues
