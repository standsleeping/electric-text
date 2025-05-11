from electric_text.tools.functions.find_tool_box_by_name import find_tool_box_by_name


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
