from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
)


def handle_text_start(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle the start of a text block in OpenAI stream responses.

    This function creates a new ContentBlock for text content and adds it to the
    StreamHistory content_blocks. It is triggered when a response.content_part.added
    event with type="output_text" is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the new content block and chunk
    """
    # For OpenAI, we start with an empty text content
    # The content will be built up through deltas
    text_content = ""

    output_index = data.get("output_index", 0)

    # Create a ContentBlock with TextData
    new_content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text=text_content),
    )

    history.content_blocks.insert(output_index, new_content_block)

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TEXT_START,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
