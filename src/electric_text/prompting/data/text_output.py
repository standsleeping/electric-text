from dataclasses import dataclass


@dataclass
class TextOutput:
    """Output for text responses."""

    content: str
