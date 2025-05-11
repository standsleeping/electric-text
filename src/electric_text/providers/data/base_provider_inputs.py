from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseProviderInputs:
    """Base inputs shared across all providers"""

    messages: list[dict[str, str]]
    model: str | None = None
    max_tokens: Optional[int] = None
