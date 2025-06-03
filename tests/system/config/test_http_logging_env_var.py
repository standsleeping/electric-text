import pytest

from electric_text.prompting.functions.get_http_logging_enabled import (
    get_http_logging_enabled,
)
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_http_logging_env_var_enabled():
    """Returns True when ELECTRIC_TEXT_HTTP_LOGGING is set to 'true'."""

    # Set environment variable to enable logging
    with mock_env({"ELECTRIC_TEXT_HTTP_LOGGING": "true"}):
        # Check if logging is enabled
        result = get_http_logging_enabled()

        # Verify logging is enabled
        assert result is True


@pytest.mark.asyncio
async def test_electric_text_http_logging_env_var_disabled():
    """Returns False when ELECTRIC_TEXT_HTTP_LOGGING is not set or set to 'false'."""

    # Set environment variable to disable logging
    with mock_env({"ELECTRIC_TEXT_HTTP_LOGGING": "false"}):
        # Check if logging is enabled
        result = get_http_logging_enabled()

        # Verify logging is disabled
        assert result is False
