import pytest

from electric_text.web.functions.get_log_level import get_log_level
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_log_level_env_var():
    """Returns ELECTRIC_TEXT_LOG_LEVEL environment variable value."""

    test_log_level = "DEBUG"

    # Set environment variable
    with mock_env({"ELECTRIC_TEXT_LOG_LEVEL": test_log_level}):
        # Get log level
        result = get_log_level()

        # Verify correct log level returned
        assert result == test_log_level
