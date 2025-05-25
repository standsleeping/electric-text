from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_text_delta(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle a text delta in OpenAI stream responses.

    This function updates the text content in a content block in the StreamHistory.
    It is triggered when a response.output_text.delta event is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the updated content block and new chunk
    """
    delta = data.get("delta", "")
    output_index = data.get("output_index", 0)

    # Get the appropriate content block and update its text
    content_block = history.content_blocks[output_index]

    # Update the text content with the delta
    text_data = content_block.data
    text_data.text += delta

    # Add a chunk to record this delta
    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TEXT_DELTA,
            raw_line=raw_line,
            parsed_data=data,
        )
    )
