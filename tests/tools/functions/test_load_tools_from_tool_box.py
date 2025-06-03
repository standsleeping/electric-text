import pytest

from electric_text.tools.functions.load_tools_from_tool_box import (
    load_tools_from_tool_box,
)
from tests.boundaries import mock_filesystem, full_tool_config, mock_env


def test_load_tools_from_tool_box():
    """Loads tools from specific tool box."""
    with mock_filesystem(full_tool_config()) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_TOOLS_DIRECTORY": str(temp_dir)}):
            test_box_tools = load_tools_from_tool_box("test_box")
            empty_box_tools = load_tools_from_tool_box("empty_box")

            assert len(test_box_tools) == 2
            assert test_box_tools[0]["name"] == "test_tool1"
            assert test_box_tools[1]["name"] == "test_tool2"

            assert len(empty_box_tools) == 0

            with pytest.raises(ValueError):
                load_tools_from_tool_box("nonexistent_box")
