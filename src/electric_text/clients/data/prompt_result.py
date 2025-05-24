from dataclasses import dataclass, field
from typing import List

from electric_text.providers.data.content_block import ContentBlock


@dataclass
class PromptResult:
    """Model response data."""

    content_blocks: List[ContentBlock] = field(default_factory=list)
