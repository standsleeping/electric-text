"""Provider capabilities module.

This module defines the capabilities that different providers may support.
"""

from electric_text.capabilities.constants import (
    STRUCTURED_OUTPUT,
    PREFILL,
    STREAMING,
    STRUCTURED_OUTPUT_FORMATS,
    PREFILL_FORMATS,
    DEFAULT_PROVIDER_CAPABILITIES,
)
from electric_text.capabilities.provider_capability import ProviderCapability
from electric_text.capabilities.provider_capabilities import ProviderCapabilities

__all__ = [
    "ProviderCapability",
    "ProviderCapabilities",
    "STRUCTURED_OUTPUT",
    "PREFILL",
    "STREAMING",
]