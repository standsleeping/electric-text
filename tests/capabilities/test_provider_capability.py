from electric_text.capabilities.provider_capability import ProviderCapability
from electric_text.capabilities.constants import (
    STRUCTURED_OUTPUT,
    PREFILL,
    STREAMING,
)


def test_structured_output_format():
    """Test getting structured output format for providers."""
    # Test with existing provider
    ollama_format = ProviderCapability.get_structured_output_format("ollama")
    assert ollama_format is not None
    assert "param" in ollama_format
    assert ollama_format["param"] == "format_schema"

    # Test with uppercase provider name (should be case insensitive)
    ollama_format_upper = ProviderCapability.get_structured_output_format("OLLAMA")
    assert ollama_format_upper == ollama_format

    # Test with non-existent provider
    nonexistent_format = ProviderCapability.get_structured_output_format("nonexistent")
    assert nonexistent_format is None


def test_prefill_format():
    """Test getting prefill format for providers."""
    # Test with existing provider
    anthropic_format = ProviderCapability.get_prefill_format("anthropic")
    assert anthropic_format is not None
    assert "param" in anthropic_format
    assert anthropic_format["param"] == "prefill_content"

    # Test with uppercase provider name (should be case insensitive)
    anthropic_format_upper = ProviderCapability.get_prefill_format("ANTHROPIC")
    assert anthropic_format_upper == anthropic_format

    # Test with non-existent provider
    nonexistent_format = ProviderCapability.get_prefill_format("nonexistent")
    assert nonexistent_format is None


def test_supports_capability_structured_output():
    """Test checking if a provider supports structured output."""
    # Test providers that support structured output
    assert ProviderCapability.supports_capability("ollama", STRUCTURED_OUTPUT)
    assert ProviderCapability.supports_capability("anthropic", STRUCTURED_OUTPUT)
    assert ProviderCapability.supports_capability("openai", STRUCTURED_OUTPUT)

    # Test with non-existent provider
    assert not ProviderCapability.supports_capability("nonexistent", STRUCTURED_OUTPUT)


def test_supports_capability_prefill():
    """Test checking if a provider supports prefill."""
    # Test provider that supports prefill
    assert ProviderCapability.supports_capability("anthropic", PREFILL)

    # Test providers that don't support prefill
    assert not ProviderCapability.supports_capability("ollama", PREFILL)
    assert not ProviderCapability.supports_capability("openai", PREFILL)

    # Test with non-existent provider
    assert not ProviderCapability.supports_capability("nonexistent", PREFILL)


def test_supports_capability_streaming():
    """Test checking if a provider supports streaming."""
    # Test providers that support streaming
    assert ProviderCapability.supports_capability("ollama", STREAMING)
    assert ProviderCapability.supports_capability("anthropic", STREAMING)
    assert ProviderCapability.supports_capability("openai", STREAMING)

    # Test with non-existent provider
    assert not ProviderCapability.supports_capability("nonexistent", STREAMING)


def test_supports_capability_unknown():
    """Test checking if a provider supports an unknown capability."""
    # Test with unknown capability
    assert not ProviderCapability.supports_capability("ollama", "unknown")
    assert not ProviderCapability.supports_capability("anthropic", "unknown")
    assert not ProviderCapability.supports_capability("openai", "unknown")
