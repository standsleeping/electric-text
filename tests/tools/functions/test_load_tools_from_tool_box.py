import pytest

from electric_text.tools.functions.load_tools_from_tool_box import (
    load_tools_from_tool_box,
)


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
