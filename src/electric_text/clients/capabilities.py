"""
This module defines the capabilities that different providers may support.
"""

from typing import Dict, Any, Optional, ClassVar, Union


class ProviderCapability:
    """
    Define standard capabilities that providers may implement.

    This class serves as a registry of known capabilities and their metadata.
    """

    STRUCTURED_OUTPUT = "structured_output"
    PREFILL = "prefill"
    STREAMING = "streaming"

    STRUCTURED_OUTPUT_FORMATS: ClassVar[
        Dict[str, Dict[str, Union[str, bool, Dict[str, str]]]]
    ] = {
        "ollama": {
            "param": "format_schema",
            "schema_method": "model_json_schema",
        },
        "anthropic": {
            "param": "structured_prefill",
            "value": True,
        },
        "openai": {
            "param": "response_format",
            "value": {"type": "json_object"},
        },
    }

    PREFILL_FORMATS: ClassVar[Dict[str, Dict[str, Any]]] = {
        "anthropic": {
            "param": "prefill_content",  # Actual content parameter
            "structured_param": "structured_prefill",  # Flag for structured prefill
            "structured_value": True,  # Default value for structured prefill flag
        }
    }

    @classmethod
    def get_structured_output_format(
        cls, provider_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the structured output format details for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary with format details or None if not supported
        """
        return cls.STRUCTURED_OUTPUT_FORMATS.get(provider_name.lower())

    @classmethod
    def get_prefill_format(cls, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the prefill format details for a provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary with format details or None if not supported
        """
        return cls.PREFILL_FORMATS.get(provider_name.lower())

    @classmethod
    def supports_capability(cls, provider_name: str, capability: str) -> bool:
        """
        Check if a provider supports a capability.

        Args:
            provider_name: Name of the provider
            capability: Capability to check

        Returns:
            True if the provider supports the capability
        """
        provider_name = provider_name.lower()

        if capability == cls.STRUCTURED_OUTPUT:
            return provider_name in cls.STRUCTURED_OUTPUT_FORMATS
        elif capability == cls.PREFILL:
            return provider_name in cls.PREFILL_FORMATS

        # Default capability support (can be expanded)
        provider_capabilities = {
            "ollama": {cls.STRUCTURED_OUTPUT, cls.STREAMING},
            "anthropic": {
                cls.STRUCTURED_OUTPUT,
                cls.STREAMING,
                cls.PREFILL,
            },
            "openai": {
                cls.STRUCTURED_OUTPUT,
                cls.STREAMING,
            },
        }

        return capability in provider_capabilities.get(provider_name, set())


# Provider-specific capability implementations
class ProviderCapabilities:
    """
    Container for the capabilities of a specific provider instance.

    This class can be used to query capabilities of a provider instance
    and retrieve implementation details.
    """

    def __init__(self, provider_name: str):
        """
        Initialize with a provider name.

        Args:
            provider_name: Name of the provider
        """
        self.provider_name = provider_name.lower()

    def supports(self, capability: str) -> bool:
        """
        Check if this provider supports a capability.

        Args:
            capability: Capability to check

        Returns:
            True if the provider supports the capability
        """
        return ProviderCapability.supports_capability(self.provider_name, capability)

    def get_capability_params(self, capability: str) -> Optional[Dict[str, Any]]:
        """
        Get provider-specific parameters for a capability.

        Args:
            capability: Capability to get parameters for

        Returns:
            Dictionary with parameter details or None if not supported
        """
        if capability == ProviderCapability.STRUCTURED_OUTPUT:
            return ProviderCapability.get_structured_output_format(self.provider_name)
        elif capability == ProviderCapability.PREFILL:
            return ProviderCapability.get_prefill_format(self.provider_name)

        # Add other capability parameter getters as needed
        return None
