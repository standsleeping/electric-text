from typing import List
from dataclasses import dataclass, field

from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
    ToolCallData,
)


@dataclass
class StreamHistory:
    chunks: List[StreamChunk] = field(default_factory=list)
    content_blocks: List[ContentBlock] = field(default_factory=list)

    def add_chunk(self, chunk: StreamChunk) -> "StreamHistory":
        self.chunks.append(chunk)
        return self

    def extract_text_content(self) -> str:
        """Extract text content from content blocks.

        Returns:
            Concatenated text content from all text blocks
        """
        if not self.content_blocks:
            return ""

        text_parts: list[str] = []
        for block in self.content_blocks:
            if block.type == ContentBlockType.TEXT:
                # Note: currently this function is ONLY used for parsing structured outputs.
                # Therefore, we ignore tool calls.
                text_data: TextData | ToolCallData = block.data
                if isinstance(text_data, TextData):
                    text_parts.append(str(text_data))

        return "".join(text_parts)

    def __str__(self) -> str:
        """String representation of StreamHistory.

        Returns:
            String representation of all content blocks joined with newlines
        """
        if not self.content_blocks:
            return "[No content]"

        return "\n".join(str(block) for block in self.content_blocks)
