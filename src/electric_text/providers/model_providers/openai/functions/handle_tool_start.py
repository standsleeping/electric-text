from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    ToolCallData,
)
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_tool_start(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle the start of a tool call in OpenAI stream responses.

    This function creates a new ContentBlock for a tool call and adds it to the
    StreamHistory content_blocks. It is triggered when a response.content_part.added
    event with type="tool_use" is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the new content block and chunk
    """
    # Extract the tool name and initial input
    part = data.get("part", {})
    name = part.get("name", "")
    input_data = part.get("input", {})

    # Use the output_index from the event data or default to the end of the list
    output_index = data.get("output_index", 0)

    # Create a ContentBlock with ToolCallData
    new_content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name=name,
            input=input_data,
            input_json_string="",  # Will be populated with deltas
        ),
    )

    history.content_blocks.insert(output_index, new_content_block)

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_START,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
