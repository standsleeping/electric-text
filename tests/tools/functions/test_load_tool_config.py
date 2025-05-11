from electric_text.tools.functions.load_tool_config import load_tool_config


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
