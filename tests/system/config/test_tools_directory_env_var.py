import pytest

from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_tools_directory_env_var():
    """Returns ELECTRIC_TEXT_TOOLS_DIRECTORY environment variable value."""

    test_tools_dir = "/custom/tools"

    # Set environment variable
    with mock_env({"ELECTRIC_TEXT_TOOLS_DIRECTORY": test_tools_dir}):
        # Get tools directory - should return env var value
        result = get_tool_configs_directory()

        # Verify correct directory returned
        assert result == test_tools_dir
