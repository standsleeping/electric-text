from electric_text.tools.functions.load_tool_boxes import load_tool_boxes


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
