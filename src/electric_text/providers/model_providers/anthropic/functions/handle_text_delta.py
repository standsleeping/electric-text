from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def handle_text_delta(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    delta = data.get("delta", {})
    content: str = delta.get("text", "")
    index = data.get("index", 0)

    content_block = history.content_blocks[index]
    text_data = content_block.data
    text_data.text += content

    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TEXT_DELTA,
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
