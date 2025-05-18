import json
from typing import Any
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory


def process_stream_response(
    raw_line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a stream response line into a StreamHistory.

    This function handles individual stream response chunks from Anthropic
    and adds the appropriate StreamChunk objects to the provided history.

    Args:
        raw_line: The raw line received from the stream
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory with the new chunk(s) added
    """
    if not raw_line.strip():
        return history

    if raw_line.startswith("event:"):
        return history

    if raw_line.startswith("data:"):
        data_str: str = raw_line[5:].strip()
        try:
            data: dict[str, Any] = json.loads(data_str)
            event_type: str = data.get("type", "")

            match event_type:
                case "content_block_delta":
                    if data.get("delta", {}).get("type") == "text_delta":
                        content: str = data.get("delta", {}).get("text", "")
                        return history.add_chunk(
                            StreamChunk(
                                type=StreamChunkType.CONTENT_CHUNK,
                                raw_line=raw_line,
                                parsed_data=data,
                                content=content,
                            )
                        )

                case "message_stop":
                    # Final message indicating completion
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.COMPLETION_END,
                            raw_line=raw_line,
                            parsed_data=data,
                            content="",
                        )
                    )

                case (
                    "message_start"
                    | "content_block_start"
                    | "ping"
                    | "content_block_stop"
                    | "message_delta"
                ):
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.INFO_MARKER,
                            raw_line=raw_line,
                            parsed_data=data,
                            content="",
                        )
                    )

                case _:
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.UNRECOGNIZED_EVENT,
                            raw_line=raw_line,
                            parsed_data=data,
                            content="",
                        )
                    )

        except json.JSONDecodeError:
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.PARSE_ERROR,
                    raw_line=raw_line,
                    parsed_data=None,
                    content="",
                )
            )
    else:
        return history.add_chunk(
            StreamChunk(
                type=StreamChunkType.UNHANDLED_LINE,
                raw_line=raw_line,
                parsed_data=None,
                content="",
            )
        )

    return history
