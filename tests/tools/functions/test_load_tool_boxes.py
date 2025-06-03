from electric_text.tools.functions.load_tool_boxes import load_tool_boxes
from tests.boundaries import mock_filesystem, full_tool_config, mock_env


def test_load_tool_boxes():
    """Loads tool boxes from tool_boxes.json file."""
    with mock_filesystem(full_tool_config()) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_TOOLS_DIRECTORY": str(temp_dir)}):
            tool_boxes = load_tool_boxes()

            assert len(tool_boxes) == 2
            assert tool_boxes[0]["name"] == "test_box"
            assert tool_boxes[0]["description"] == "Test tool box"
            assert len(tool_boxes[0]["tools"]) == 2

            assert tool_boxes[1]["name"] == "empty_box"
            assert tool_boxes[1]["description"] == "Empty tool box"
            assert len(tool_boxes[1]["tools"]) == 0
