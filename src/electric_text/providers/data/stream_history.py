from dataclasses import dataclass, field
from typing import List

from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


@dataclass
class StreamHistory:
    chunks: List[StreamChunk] = field(default_factory=list)

    def add_chunk(self, chunk: StreamChunk) -> "StreamHistory":
        self.chunks.append(chunk)
        return self

    def get_full_content(self) -> str:
        """
        Rebuilds the full content from the stream history by concatenating
        all content chunks in order.

        Returns:
            str: The complete content from all content chunks
        """
        content_parts = []
        for chunk in self.chunks:
            if (
                chunk.type
                in [
                    StreamChunkType.PREFILLED_CONTENT,
                    StreamChunkType.CONTENT_CHUNK,
                ]
                and chunk.content
            ):
                content_parts.append(chunk.content)
        return "".join(content_parts)
