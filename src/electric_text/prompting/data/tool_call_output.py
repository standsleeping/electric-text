from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCallOutput:
    """Output for tool call responses."""

    name: str
    inputs: dict[str, Any]
    output: Any | None = None
