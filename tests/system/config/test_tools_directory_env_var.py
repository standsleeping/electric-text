import pytest
from tempfile import TemporaryDirectory

from electric_text.tools.functions.get_tool_configs_directory import (
    get_tool_configs_directory,
)


@pytest.mark.asyncio
async def test_electric_text_tools_directory_env_var(monkeypatch):
    """Returns ELECTRIC_TEXT_TOOLS_DIRECTORY environment variable value."""

    # Create temporary directory
    with TemporaryDirectory() as temp_dir:
        # Set environment variable
        monkeypatch.setenv("ELECTRIC_TEXT_TOOLS_DIRECTORY", temp_dir)

        # Get tools directory - should return env var value
        result = get_tool_configs_directory()

        # Verify correct directory returned
        assert result == temp_dir
