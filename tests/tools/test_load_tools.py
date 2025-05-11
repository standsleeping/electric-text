import pytest

from electric_text.tools.functions.load_tools import (
    get_tool_configs_directory,
    load_tool_boxes,
    load_tool_config,
    validate_tool_box,
    find_tool_box_by_name,
    load_tools_from_tool_box,
    load_tools_from_tool_boxes,
)


def test_get_tool_configs_directory(temp_tool_configs_dir):
    """Test that get_tool_configs_directory returns the correct directory."""
    config_dir = get_tool_configs_directory()
    assert config_dir == temp_tool_configs_dir


def test_load_tool_boxes(temp_tool_configs_dir):
    """Test loading tool boxes from the tool_boxes.json file."""
    tool_boxes = load_tool_boxes()

    assert len(tool_boxes) == 2
    assert tool_boxes[0]["name"] == "test_box"
    assert tool_boxes[0]["description"] == "Test tool box"
    assert len(tool_boxes[0]["tools"]) == 2

    assert tool_boxes[1]["name"] == "empty_box"
    assert tool_boxes[1]["description"] == "Empty tool box"
    assert len(tool_boxes[1]["tools"]) == 0


def test_load_tool_config(temp_tool_configs_dir):
    """Test loading a specific tool config by name."""
    tool1 = load_tool_config("test_tool1")
    tool2 = load_tool_config("test_tool2")
    nonexistent_tool = load_tool_config("nonexistent_tool")

    assert tool1 is not None
    assert tool1["name"] == "test_tool1"
    assert tool1["description"] == "Test tool 1"

    assert tool2 is not None
    assert tool2["name"] == "test_tool2"
    assert tool2["description"] == "Test tool 2"

    assert nonexistent_tool is None


def test_validate_tool_box():
    """Test validation of tool box configurations."""
    valid_tool_box = {
        "name": "valid_box",
        "description": "Valid tool box",
        "tools": ["tool1", "tool2"],
    }

    missing_name = {"description": "Missing name", "tools": ["tool1"]}

    missing_tools = {"name": "missing_tools", "description": "Missing tools"}

    invalid_tools = {
        "name": "invalid_tools",
        "description": "Invalid tools",
        "tools": "not_a_list",
    }

    assert validate_tool_box(valid_tool_box) is True
    assert validate_tool_box(missing_name) is False
    assert validate_tool_box(missing_tools) is False
    assert validate_tool_box(invalid_tools) is False
    assert validate_tool_box("not_a_dict") is False


def test_find_tool_box_by_name(temp_tool_configs_dir):
    """Test finding a tool box by name."""
    test_box = find_tool_box_by_name("test_box")
    empty_box = find_tool_box_by_name("empty_box")
    nonexistent_box = find_tool_box_by_name("nonexistent_box")

    assert test_box is not None
    assert test_box["name"] == "test_box"
    assert len(test_box["tools"]) == 2

    assert empty_box is not None
    assert empty_box["name"] == "empty_box"
    assert len(empty_box["tools"]) == 0

    assert nonexistent_box is None


def test_load_tools_from_tool_box(temp_tool_configs_dir):
    """Test loading tools from a specific tool box."""
    test_box_tools = load_tools_from_tool_box("test_box")
    empty_box_tools = load_tools_from_tool_box("empty_box")

    assert len(test_box_tools) == 2
    assert test_box_tools[0]["name"] == "test_tool1"
    assert test_box_tools[1]["name"] == "test_tool2"

    assert len(empty_box_tools) == 0

    with pytest.raises(ValueError):
        load_tools_from_tool_box("nonexistent_box")


def test_load_tools_from_tool_boxes(temp_tool_configs_dir):
    """Test loading tools from multiple tool boxes."""
    all_tools = load_tools_from_tool_boxes(["test_box", "empty_box"])
    only_test_box = load_tools_from_tool_boxes(["test_box"])
    only_empty_box = load_tools_from_tool_boxes(["empty_box"])
    nonexistent_box = load_tools_from_tool_boxes(["nonexistent_box"])
    mixed_boxes = load_tools_from_tool_boxes(["test_box", "nonexistent_box"])

    assert len(all_tools) == 2
    assert len(only_test_box) == 2
    assert len(only_empty_box) == 0
    assert len(nonexistent_box) == 0
    assert len(mixed_boxes) == 2  # Should still load tools from valid boxes
