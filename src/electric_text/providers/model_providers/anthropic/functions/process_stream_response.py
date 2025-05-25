import json
from typing import Any
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.model_providers.anthropic.functions.handle_tool_start import (
    handle_tool_start,
)
from electric_text.providers.model_providers.anthropic.functions.handle_text_start import (
    handle_text_start,
)
from electric_text.providers.model_providers.anthropic.functions.handle_tool_delta import (
    handle_tool_delta,
)
from electric_text.providers.model_providers.anthropic.functions.handle_text_delta import (
    handle_text_delta,
)


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
                case "message_start":
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.STREAM_START,
                            raw_line=raw_line,
                            parsed_data=data,
                        )
                    )

                case "content_block_start":
                    content_block = data.get("content_block", {})
                    content_block_type = content_block.get("type", "")
                    if content_block_type == "tool_use":
                        return handle_tool_start(raw_line, data, history)
                    elif content_block_type == "text":
                        return handle_text_start(raw_line, data, history)
                    else:
                        return history.add_chunk(
                            StreamChunk(
                                type=StreamChunkType.UNHANDLED_EVENT,
                                raw_line=raw_line,
                                parsed_data=data,
                            )
                        )

                case "content_block_delta":
                    delta = data.get("delta", {})
                    delta_type = delta.get("type", "")
                    if delta_type == "input_json_delta":
                        return handle_tool_delta(raw_line, data, history)
                    elif delta_type == "text_delta":
                        return handle_text_delta(raw_line, data, history)
                    else:
                        return history.add_chunk(
                            StreamChunk(
                                type=StreamChunkType.UNHANDLED_EVENT,
                                raw_line=raw_line,
                                parsed_data=data,
                            )
                        )

                case "message_stop":
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.STREAM_STOP,
                            raw_line=raw_line,
                            parsed_data=data,
                        )
                    )

                case _:
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.UNHANDLED_EVENT,
                            raw_line="",
                            parsed_data=data,
                        )
                    )

        except json.JSONDecodeError:
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.PARSE_ERROR,
                    raw_line=raw_line,
                    parsed_data=None,
                )
            )
    else:
        return history.add_chunk(
            StreamChunk(
                type=StreamChunkType.UNHANDLED_EVENT,
                raw_line=raw_line,
                parsed_data=None,
            )
        )
