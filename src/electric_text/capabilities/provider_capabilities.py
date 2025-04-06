"""Provider-specific capability implementations."""

from typing import Dict, Any, Optional

from electric_text.capabilities.provider_capability import ProviderCapability


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
