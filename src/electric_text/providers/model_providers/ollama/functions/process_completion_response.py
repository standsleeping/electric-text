import json
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

    data = json.loads(line)

    # Extract message data
    message = data.get("message", {})
    content = message.get("content")
    tool_calls = message.get("tool_calls")

    # Process tool calls if present
    if tool_calls:
        for tool_call in tool_calls:
            history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.FULL_TOOL_CALL,
                    raw_line=line,
                    parsed_data=tool_call,
                    content=json.dumps(tool_call.get("function", {})),
                )
            )

    if content:
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.CONTENT_CHUNK,
                raw_line=line,
                parsed_data=data,
                content=content,
            )
        )

    if data.get("done", False):
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.COMPLETION_END,
                raw_line=line,
            )
        )

    return history
