from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    ToolCallData,
)
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_function_call_start(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle the start of a function call in OpenAI stream responses.

    This function creates a new ContentBlock for a function call and adds it to the
    StreamHistory content_blocks. It is triggered when a response.output_item.added
    event with type="function_call" is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the new content block and chunk
    """
    item = data.get("item", {})
    name = item.get("name", "")

    new_content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name=name,
            input={},  # Will be populated when arguments are complete
            input_json_string="",  # Will be populated with deltas
        ),
    )

    history.content_blocks.append(new_content_block)

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_START,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
