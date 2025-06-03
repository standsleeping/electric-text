import pytest

from electric_text.clients.functions.resolve_api_key import resolve_api_key
from tests.boundaries import mock_env


@pytest.mark.asyncio
async def test_electric_text_provider_api_key_env_var():
    """Resolves API key from ELECTRIC_TEXT_{PROVIDER}_API_KEY environment variable."""

    test_api_key = "test-api-key-123"

    # Set environment variable for anthropic provider
    with mock_env({"ELECTRIC_TEXT_ANTHROPIC_API_KEY": test_api_key}):
        # Resolve API key for anthropic provider
        resolved_key = resolve_api_key("anthropic")

        # Verify correct API key returned
        assert resolved_key == test_api_key
