from dataclasses import dataclass
from typing import Optional


@dataclass
class BaseProviderInputs:
    """Base inputs shared across all providers"""

    model: str | None = None
    max_tokens: Optional[int] = None
