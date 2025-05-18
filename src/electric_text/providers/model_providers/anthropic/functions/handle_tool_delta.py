from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_tool_delta(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    delta = data.get("delta", {})
    index = data.get("index", 0)
    partial_json = delta.get("partial_json", {})

    content_block = history.content_blocks[index]

    # Note: the `name` of the tool call is assumed to be produced in full during TOOL_START.
    # The `input` now gets completed in chunks.
    # Append the partial json to the input of the tool call
    content_block.data.input_json_string += partial_json

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_DELTA,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
