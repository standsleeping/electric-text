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
    index: int = data.get("index", 0)
    content_block: dict[str, Any] = data.get("content_block", {})
    name: str = content_block.get("name", "")
    input: dict[str, Any] = content_block.get("input", {})

    new_content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name=name,
            input=input,
            input_json_string="",
        ),
    )

    history.content_blocks.insert(index, new_content_block)

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_START,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
