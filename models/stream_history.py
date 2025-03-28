import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Any


class StreamChunkType(Enum):
    INITIAL_MESSAGE = "initial_message"  # First chunk with role/content
    CONTENT_CHUNK = "content_chunk"  # Regular content chunk
    COMPLETION_END = "completion_end"  # Empty delta with finish_reason "stop"
    STREAM_DONE = "stream_done"  # [DONE] marker
    EMPTY_LINE = "empty_line"  # Empty line
    INVALID_FORMAT = "invalid_format"  # Does not start with "data: "
    NO_CHOICES = "no_choices"  # Missing choices array
    PARSE_ERROR = "parse_error"  # JSON parse error
    COMPLETE_RESPONSE = "COMPLETE_RESPONSE"  # Non-streaming response
    HTTP_ERROR = "HTTP_ERROR"  # HTTP error
    FORMAT_ERROR = "FORMAT_ERROR"  # Response format doesn't match expected schema


@dataclass
class StreamChunk:
    type: StreamChunkType
    raw_line: str
    parsed_data: Optional[dict[str, str]] = None
    content: Optional[str] = None
    error: Optional[str] = None


@dataclass
class StreamHistory:
    chunks: List[StreamChunk] = field(default_factory=list)

    def add_chunk(self, chunk: StreamChunk) -> None:
        self.chunks.append(chunk)

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
                in [StreamChunkType.CONTENT_CHUNK, StreamChunkType.COMPLETE_RESPONSE]
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


def categorize_stream_line(line: str) -> StreamChunk:
    """
    Categorize a stream line from an LLM provider into a StreamChunk.

    Args:
        line: Raw line from the stream

    Returns:
        StreamChunk containing the categorized data
    """
    if not line:
        return StreamChunk(StreamChunkType.EMPTY_LINE, line)

    if line.startswith("data: [DONE]"):
        return StreamChunk(StreamChunkType.STREAM_DONE, line)

    if not line.startswith("data: "):
        return StreamChunk(StreamChunkType.INVALID_FORMAT, line)

    try:
        data = json.loads(line[6:])  # Remove "data: " prefix
        if not data.get("choices"):
            return StreamChunk(StreamChunkType.NO_CHOICES, line, parsed_data=data)

        delta = data["choices"][0]["delta"]

        # Initial message
        if "role" in delta:
            return StreamChunk(
                StreamChunkType.INITIAL_MESSAGE,
                line,
                parsed_data=data,
                content=delta.get("content", ""),
            )

        # Completion end
        if not delta and data["choices"][0].get("finish_reason") == "stop":
            return StreamChunk(StreamChunkType.COMPLETION_END, line, parsed_data=data)

        # Content chunk
        content = delta.get("content")
        if content:
            return StreamChunk(
                StreamChunkType.CONTENT_CHUNK,
                line,
                parsed_data=data,
                content=content,
            )

        return StreamChunk(StreamChunkType.NO_CHOICES, line, parsed_data=data)

    except json.JSONDecodeError as e:
        return StreamChunk(StreamChunkType.PARSE_ERROR, line, error=str(e))
