"""Provider capability definitions and registry."""

from typing import Dict, Any, Optional

from electric_text.capabilities.constants import (
    STRUCTURED_OUTPUT,
    PREFILL,
    STRUCTURED_OUTPUT_FORMATS,
    PREFILL_FORMATS,
    DEFAULT_PROVIDER_CAPABILITIES,
)


class ProviderCapability:
    """
    Define standard capabilities that providers may implement.

    This class serves as a registry of known capabilities and their metadata.
    """

    STRUCTURED_OUTPUT = STRUCTURED_OUTPUT
    PREFILL = PREFILL
    STREAMING = "streaming"

    STRUCTURED_OUTPUT_FORMATS = STRUCTURED_OUTPUT_FORMATS
    PREFILL_FORMATS = PREFILL_FORMATS

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

        # Default capability support
        return capability in DEFAULT_PROVIDER_CAPABILITIES.get(provider_name, set())
