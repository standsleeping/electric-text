from electric_text.capabilities.constants import (
    STRUCTURED_OUTPUT,
    PREFILL,
    STREAMING,
    STRUCTURED_OUTPUT_FORMATS,
    PREFILL_FORMATS,
    DEFAULT_PROVIDER_CAPABILITIES,
)


def test_capability_constants():
    """Test that capability constants are defined correctly."""
    assert STRUCTURED_OUTPUT == "structured_output"
    assert PREFILL == "prefill"
    assert STREAMING == "streaming"


def test_structured_output_formats():
    """Test that structured output formats are defined for providers."""
    assert "ollama" in STRUCTURED_OUTPUT_FORMATS
    assert "anthropic" in STRUCTURED_OUTPUT_FORMATS
    assert "openai" in STRUCTURED_OUTPUT_FORMATS

    # Check format for Ollama
    ollama_format = STRUCTURED_OUTPUT_FORMATS["ollama"]
    assert "param" in ollama_format
    assert ollama_format["param"] == "format_schema"
    assert ollama_format["schema_method"] == "model_json_schema"

    # Check format for Anthropic
    anthropic_format = STRUCTURED_OUTPUT_FORMATS["anthropic"]
    assert "param" in anthropic_format
    assert anthropic_format["param"] == "structured_prefill"
    assert anthropic_format["value"] is True

    # Check format for OpenAI
    openai_format = STRUCTURED_OUTPUT_FORMATS["openai"]
    assert "param" in openai_format
    assert openai_format["param"] == "response_format"
    assert openai_format["value"] == {"type": "json_object"}


def test_prefill_formats():
    """Test that prefill formats are defined correctly."""
    assert "anthropic" in PREFILL_FORMATS

    anthropic_format = PREFILL_FORMATS["anthropic"]
    assert "param" in anthropic_format
    assert anthropic_format["param"] == "prefill_content"
    assert anthropic_format["structured_param"] == "structured_prefill"
    assert anthropic_format["structured_value"] is True


def test_default_provider_capabilities():
    """Test that default provider capabilities are defined correctly."""
    assert "ollama" in DEFAULT_PROVIDER_CAPABILITIES
    assert "anthropic" in DEFAULT_PROVIDER_CAPABILITIES
    assert "openai" in DEFAULT_PROVIDER_CAPABILITIES

    # Check ollama capabilities
    ollama_caps = DEFAULT_PROVIDER_CAPABILITIES["ollama"]
    assert STRUCTURED_OUTPUT in ollama_caps
    assert STREAMING in ollama_caps
    assert PREFILL not in ollama_caps

    # Check anthropic capabilities
    anthropic_caps = DEFAULT_PROVIDER_CAPABILITIES["anthropic"]
    assert STRUCTURED_OUTPUT in anthropic_caps
    assert STREAMING in anthropic_caps
    assert PREFILL in anthropic_caps

    # Check openai capabilities
    openai_caps = DEFAULT_PROVIDER_CAPABILITIES["openai"]
    assert STRUCTURED_OUTPUT in openai_caps
    assert STREAMING in openai_caps
    assert PREFILL not in openai_caps
