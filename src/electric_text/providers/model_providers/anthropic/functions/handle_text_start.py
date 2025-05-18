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
    content_block = data.get("content_block", {})
    index = data.get("index", 0)
    text_content = content_block.get("text", "")

    # Create a ContentBlock with TextData
    new_content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text=text_content),
    )

    history.content_blocks.insert(index, new_content_block)

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TEXT_START,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
