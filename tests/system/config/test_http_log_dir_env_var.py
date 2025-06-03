import pytest

from electric_text.prompting.functions.get_http_log_dir import get_http_log_dir
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_http_log_dir_env_var():
    """Returns ELECTRIC_TEXT_HTTP_LOG_DIR environment variable value as Path."""

    test_log_dir = "/custom/http/logs"

    # Set environment variable
    with mock_env({"ELECTRIC_TEXT_HTTP_LOG_DIR": test_log_dir}):
        # Get HTTP log directory
        result = get_http_log_dir()

        # Verify correct directory returned
        assert result == test_log_dir
