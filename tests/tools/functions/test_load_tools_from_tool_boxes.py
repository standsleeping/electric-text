from electric_text.tools.functions.load_tools_from_tool_boxes import (
    load_tools_from_tool_boxes,
)


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
