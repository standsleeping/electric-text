from dataclasses import dataclass


@dataclass
class BaseProviderInputs:
    """Base inputs shared across all providers"""

    messages: list[dict[str, str]]
    model: str | None = None
