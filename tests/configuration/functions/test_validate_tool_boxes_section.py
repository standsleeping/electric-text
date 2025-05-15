from electric_text.configuration.functions.validate_tool_boxes_section import validate_tool_boxes_section


def test_validate_tool_boxes_section_valid() -> None:
    """Returns no issues for valid tool_boxes configuration."""
    tool_boxes = {"default": ["tool1", "tool2"], "advanced": ["tool3"]}
    issues = validate_tool_boxes_section(tool_boxes)
    assert issues == []


def test_validate_tool_boxes_section_invalid_tools() -> None:
    """Returns issues for invalid tools list (not a list)."""
    tool_boxes = {"default": "not_a_list", "advanced": ["tool3"]}
    issues = validate_tool_boxes_section(tool_boxes)
    assert len(issues) == 1
    assert "Invalid tools list" in issues[0]
    assert "default" in issues[0]


def test_validate_tool_boxes_section_multiple_invalid() -> None:
    """Returns multiple issues for multiple invalid tool boxes."""
    tool_boxes = {"default": "not_a_list", "advanced": {"key": "value"}}
    issues = validate_tool_boxes_section(tool_boxes)
    assert len(issues) == 2
    assert any("default" in issue for issue in issues)
    assert any("advanced" in issue for issue in issues)