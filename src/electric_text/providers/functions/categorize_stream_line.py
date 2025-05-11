import json
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


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
