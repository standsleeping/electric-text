from electric_text.tools.functions.find_tool_box_by_name import find_tool_box_by_name
from tests.boundaries import mock_filesystem, full_tool_config, mock_env


def test_find_tool_box_by_name():
    """Finds tool box by name."""
    with mock_filesystem(full_tool_config()) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_TOOLS_DIRECTORY": str(temp_dir)}):
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
