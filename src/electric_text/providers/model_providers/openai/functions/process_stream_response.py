import json
from typing import Any

from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.model_providers.openai.functions.handle_text_start import (
    handle_text_start,
)
from electric_text.providers.model_providers.openai.functions.handle_text_delta import (
    handle_text_delta,
)

from electric_text.providers.model_providers.openai.functions.handle_function_call_start import (
    handle_function_call_start,
)
from electric_text.providers.model_providers.openai.functions.handle_function_call_arguments_delta import (
    handle_function_call_arguments_delta,
)
from electric_text.providers.model_providers.openai.functions.handle_function_call_arguments_done import (
    handle_function_call_arguments_done,
)


def process_stream_response(
    raw_line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a stream response line into a StreamHistory.

    This function handles individual stream response chunks from OpenAI
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
                case "response.created":
                    return history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.STREAM_START,
                            raw_line=raw_line,
                            parsed_data=data,
                        )
                    )
                case "response.content_part.added":
                    part = data.get("part", "")
                    content_type = part.get("type", "")
                    if content_type == "output_text":
                        return handle_text_start(raw_line, data, history)
                    else:
                        return history.add_chunk(
                            StreamChunk(
                                type=StreamChunkType.UNHANDLED_EVENT,
                                raw_line=raw_line,
                                parsed_data=data,
                            )
                        )
                case "response.output_item.added":
                    item = data.get("item", {})
                    item_type = item.get("type", "")
                    if item_type == "function_call":
                        return handle_function_call_start(raw_line, data, history)
                    else:
                        return history.add_chunk(
                            StreamChunk(
                                type=StreamChunkType.UNHANDLED_EVENT,
                                raw_line=raw_line,
                                parsed_data=data,
                            )
                        )
                case "response.output_text.delta":
                    return handle_text_delta(raw_line, data, history)
                case "response.function_call_arguments.delta":
                    return handle_function_call_arguments_delta(raw_line, data, history)
                case "response.function_call_arguments.done":
                    return handle_function_call_arguments_done(raw_line, data, history)
                case "response.done":
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