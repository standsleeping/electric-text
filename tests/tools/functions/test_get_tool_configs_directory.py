from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)


def test_get_tool_configs_directory(temp_tool_configs_dir):
    """Test that get_tool_configs_directory returns the correct directory."""
    config_dir = get_tool_configs_directory()
    assert config_dir == temp_tool_configs_dir
