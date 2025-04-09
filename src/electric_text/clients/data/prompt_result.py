from dataclasses import dataclass


@dataclass
class PromptResult:
    """Model response data."""

    raw_content: str
