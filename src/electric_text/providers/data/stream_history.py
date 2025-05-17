import json
from dataclasses import dataclass, field
from typing import List, Any

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
                    StreamChunkType.CONTENT_CHUNK,
                    StreamChunkType.COMPLETE_RESPONSE,
                    StreamChunkType.PREFILLED_CONTENT,
                ]
                and chunk.content
            ):
                content_parts.append(chunk.content)
        return "".join(content_parts)

    @classmethod
    def from_complete_response(cls, response_data: dict[str, Any]) -> "StreamHistory":
        """
        Creates a StreamHistory from a complete (non-streaming) response.

        Args:
            response_data: The complete response data from the API

        Returns:
            StreamHistory containing the complete response as a single chunk
        """
        history = cls()

        if not response_data.get("choices"):
            chunk = StreamChunk(
                StreamChunkType.NO_CHOICES,
                raw_line=json.dumps(response_data),
                parsed_data=response_data,
            )
        else:
            message = response_data["choices"][0]["message"]
            chunk = StreamChunk(
                StreamChunkType.COMPLETE_RESPONSE,
                raw_line=json.dumps(response_data),
                parsed_data=response_data,
                content=message.get("content", ""),
            )

        history.add_chunk(chunk)
        return history
