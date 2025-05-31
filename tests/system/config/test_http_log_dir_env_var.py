import pytest
from tempfile import TemporaryDirectory

from electric_text.prompting.functions.get_http_log_dir import get_http_log_dir


@pytest.mark.asyncio
async def test_electric_text_http_log_dir_env_var(monkeypatch):
    """Returns ELECTRIC_TEXT_HTTP_LOG_DIR environment variable value as Path."""

    # Create temporary directory
    with TemporaryDirectory() as temp_dir:
        # Set environment variable
        monkeypatch.setenv("ELECTRIC_TEXT_HTTP_LOG_DIR", temp_dir)

        # Get HTTP log directory
        result = get_http_log_dir()

        # Verify correct directory returned
        assert result == temp_dir
