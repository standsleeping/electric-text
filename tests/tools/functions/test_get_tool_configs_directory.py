from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)
from tests.boundaries import mock_filesystem, full_tool_config, mock_env


def test_get_tool_configs_directory():
    """Returns correct tool configs directory."""
    with mock_filesystem(full_tool_config()) as temp_dir:
        with mock_env({"ELECTRIC_TEXT_TOOLS_DIRECTORY": str(temp_dir)}):
            config_dir = get_tool_configs_directory()
            assert config_dir == str(temp_dir)
