from unittest.mock import patch

from electric_text.capabilities import ProviderCapability, ProviderCapabilities


def test_init():
    """Test initialization of ProviderCapabilities."""
    # Test with lowercase provider name
    caps = ProviderCapabilities("ollama")
    assert caps.provider_name == "ollama"

    # Test with uppercase provider name (should be converted to lowercase)
    caps_upper = ProviderCapabilities("OLLAMA")
    assert caps_upper.provider_name == "ollama"


def test_supports():
    """Test checking if a provider supports a capability."""
    caps = ProviderCapabilities("anthropic")

    # Mock ProviderCapability.supports_capability to avoid testing the same function again
    with patch.object(ProviderCapability, "supports_capability") as mock_supports:
        # Set up return values for different capabilities
        mock_supports.side_effect = (
            lambda provider, capability: {
                "anthropic": {
                    "structured_output": True,
                    "prefill": True,
                    "streaming": True,
                    "unknown": False,
                }
            }.get(provider, {}).get(capability, False)
        )

        # Test supported capabilities
        assert caps.supports("structured_output")
        assert caps.supports("prefill")
        assert caps.supports("streaming")

        # Test unsupported capability
        assert not caps.supports("unknown")

        # Verify the mock was called with the right parameters
        mock_supports.assert_called_with("anthropic", "unknown")


def test_get_capability_params():
    """Test getting capability parameters for a provider."""
    caps = ProviderCapabilities("anthropic")

    # Create mock return values for the ProviderCapability methods
    structured_output_params = {"param": "structured_prefill", "value": True}
    prefill_params = {"param": "prefill_content"}

    # Mock the ProviderCapability methods
    with patch.object(
        ProviderCapability,
        "get_structured_output_format",
        return_value=structured_output_params,
    ) as mock_so:
        with patch.object(
            ProviderCapability, "get_prefill_format", return_value=prefill_params
        ) as mock_prefill:
            # Test getting structured output parameters
            params = caps.get_capability_params(ProviderCapability.STRUCTURED_OUTPUT)
            assert params == structured_output_params
            mock_so.assert_called_with("anthropic")

            # Test getting prefill parameters
            params = caps.get_capability_params(ProviderCapability.PREFILL)
            assert params == prefill_params
            mock_prefill.assert_called_with("anthropic")

            # Test getting parameters for unknown capability
            params = caps.get_capability_params("unknown")
            assert params is None
