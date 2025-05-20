from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_tool_delta(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle a tool call delta in OpenAI stream responses.

    This function updates the tool call input in a content block in the StreamHistory.
    It is triggered when a response.tool_input.delta event is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the updated content block and new chunk
    """
    delta = data.get("delta", "")
    output_index = data.get("output_index", 0)

    # Get the appropriate content block and update its input_json_string
    content_block = history.content_blocks[output_index]

    # Update the input_json_string with the delta
    content_block.data.input_json_string += delta

    # Add a chunk to record this delta
    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_DELTA,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
