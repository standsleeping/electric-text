from dataclasses import dataclass


@dataclass
class BaseProviderInputs:
    """Base inputs shared across all providers"""

    model: str
