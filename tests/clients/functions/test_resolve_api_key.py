from electric_text.clients.functions.resolve_api_key import resolve_api_key
from tests.boundaries import mock_env


def test_explicit_api_key():
    """Test that explicit API key is returned when provided."""
    result = resolve_api_key("openai", explicit_api_key="test-key-123")
    assert result == "test-key-123"


def test_env_variable_api_key():
    """Test that environment variable is used when no explicit key is provided."""
    with mock_env({"ELECTRIC_TEXT_OPENAI_API_KEY": "env-key-456"}):
        result = resolve_api_key("openai")
        assert result == "env-key-456"


def test_case_insensitive_provider_name():
    """Test that provider name is case insensitive for env variable lookup."""
    # Test with lowercase provider name
    with mock_env({"ELECTRIC_TEXT_OPENAI_API_KEY": "env-key-789"}):
        result = resolve_api_key("openai")
        assert result == "env-key-789"

    # Test with mixed case provider name
    with mock_env({"ELECTRIC_TEXT_OPENAI_API_KEY": "env-key-789"}):
        result = resolve_api_key("OpenAI")
        assert result == "env-key-789"


def test_explicit_key_precedence():
    """Test that explicit key takes precedence over environment variable."""
    with mock_env({"ELECTRIC_TEXT_OPENAI_API_KEY": "env-key-789"}):
        result = resolve_api_key("openai", explicit_api_key="explicit-key-999")
        assert result == "explicit-key-999"


def test_no_api_key():
    """Test that None is returned when no key is available."""
    # Remove any existing env variable for the test
    with mock_env({}, clear_prefix="ELECTRIC_TEXT_"):
        result = resolve_api_key("openai")
        assert result is None


def test_different_providers():
    """Test with different provider names."""
    with mock_env({
        "ELECTRIC_TEXT_ANTHROPIC_API_KEY": "anthropic-key",
        "ELECTRIC_TEXT_OPENAI_API_KEY": "openai-key",
        "ELECTRIC_TEXT_OLLAMA_API_KEY": "ollama-key",
    }):
        assert resolve_api_key("anthropic") == "anthropic-key"
        assert resolve_api_key("openai") == "openai-key"
        assert resolve_api_key("ollama") == "ollama-key"


def test_custom_provider():
    """Test that arbitrary provider names work."""
    with mock_env({"ELECTRIC_TEXT_CUSTOM_PROVIDER_API_KEY": "custom-key"}):
        assert resolve_api_key("custom_provider") == "custom-key"
