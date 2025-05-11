from electric_text.tools.functions.validate_tool_box import validate_tool_box


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
