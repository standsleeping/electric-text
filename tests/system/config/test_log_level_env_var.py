import pytest

from electric_text.web.functions.get_log_level import get_log_level


@pytest.mark.asyncio
async def test_electric_text_log_level_env_var(monkeypatch):
    """Returns ELECTRIC_TEXT_LOG_LEVEL environment variable value."""

    test_log_level = "DEBUG"

    # Set environment variable
    monkeypatch.setenv("ELECTRIC_TEXT_LOG_LEVEL", test_log_level)

    # Get log level
    result = get_log_level()

    # Verify correct log level returned
    assert result == test_log_level
