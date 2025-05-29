import pytest

from electric_text.providers.functions.is_http_logging_enabled import (
    is_http_logging_enabled,
)


@pytest.mark.asyncio
async def test_electric_text_http_logging_env_var_enabled(monkeypatch):
    """Returns True when ELECTRIC_TEXT_HTTP_LOGGING is set to 'true'."""

    # Set environment variable to enable logging
    monkeypatch.setenv("ELECTRIC_TEXT_HTTP_LOGGING", "true")

    # Check if logging is enabled
    result = is_http_logging_enabled()

    # Verify logging is enabled
    assert result is True


@pytest.mark.asyncio
async def test_electric_text_http_logging_env_var_disabled(monkeypatch):
    """Returns False when ELECTRIC_TEXT_HTTP_LOGGING is not set or set to 'false'."""

    # Set environment variable to disable logging
    monkeypatch.setenv("ELECTRIC_TEXT_HTTP_LOGGING", "false")

    # Check if logging is enabled
    result = is_http_logging_enabled()

    # Verify logging is disabled
    assert result is False
