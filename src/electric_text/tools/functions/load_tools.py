import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


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
