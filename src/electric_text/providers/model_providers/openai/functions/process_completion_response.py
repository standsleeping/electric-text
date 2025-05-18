import json
from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def process_completion_response(
    line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a completion response into a StreamHistory.

    Args:
        line: Line to process
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory containing all chunks from the response
    """

    data: dict[str, Any] = json.loads(line)
    output = data.get("output", [])
    first_output = output[0]
    content = first_output.get("content", [])
    first_content = content[0]
    text_content = first_content.get("text", "")

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.CONTENT_CHUNK,
            raw_line=line,
            parsed_data=data,
            content=text_content,
        )
    )
