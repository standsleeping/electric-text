from dataclasses import dataclass
from typing import Any


@dataclass
class DataOutput:
    """Output for structured data responses."""

    data: dict[str, Any]
    is_valid: bool
    schema_name: str | None = None
    validation_error: str | None = None
