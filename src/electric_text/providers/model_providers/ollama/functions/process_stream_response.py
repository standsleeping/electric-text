import json
from typing import Dict, Any
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory


def process_stream_response(
    chunk_data: Dict[str, Any],
    raw_line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a stream response chunk into a StreamHistory.

    This function handles individual stream response chunks from Ollama
    and adds the appropriate StreamChunk objects to the provided history.

    Args:
        chunk_data: The parsed JSON chunk data
        raw_line: The raw line received from the stream
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory with the new chunk(s) added
    """
    # Extract message data
    message = chunk_data.get("message", {})
    content = message.get("content")
    tool_calls = message.get("tool_calls")

    # Process tool calls if present
    if tool_calls:
        # Process each tool call
        for tool_call in tool_calls:
            history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA,
                    raw_line=raw_line,
                    parsed_data=tool_call,
                    content=json.dumps(tool_call.get("function", {})),
                )
            )

        # Mark function call arguments as done
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE,
                raw_line=raw_line,
                parsed_data=tool_calls,
                content="",
            )
        )

    # Process content if present - do this regardless of tool calls
    if content:
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.CONTENT_CHUNK,
                raw_line=raw_line,
                parsed_data=chunk_data,
                content=content,
            )
        )

    # Check for done flag
    if chunk_data.get("done", False):
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.COMPLETION_END,
                raw_line=raw_line,
                parsed_data=chunk_data,
                content="",
            )
        )

    return history
