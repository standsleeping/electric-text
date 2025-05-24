from dataclasses import dataclass, field
from typing import List

from electric_text.providers.data.content_block import ContentBlock
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


@dataclass
class StreamHistory:
    chunks: List[StreamChunk] = field(default_factory=list)
    content_blocks: List[ContentBlock] = field(default_factory=list)

    def add_chunk(self, chunk: StreamChunk) -> "StreamHistory":
        self.chunks.append(chunk)
        return self

