import json
from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType


def process_completion_response(
    line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a completion response into a StreamHistory.

    Args:
        line: Line to process
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory containing all chunks from the response
    """

    data: dict[str, Any] = json.loads(line)
    content: list[dict[str, Any]] = data.get("content", [])

    stop_reason = data.get("stop_reason")

    match stop_reason:
        case "tool_use":
            history = add_content_to_history(history, content)
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.TOOL_CALL,
                    raw_line=line,
                    parsed_data=data,
                    content="",
                )
            )
        case "end_turn":
            raw_content: str = data["content"][0]["text"]
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.CONTENT_CHUNK,
                    raw_line=line,
                    parsed_data=data,
                    content=raw_content,
                )
            )
        case _:
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.UNRECOGNIZED_EVENT,
                    raw_line=line,
                    parsed_data=data,
                    content="",
                )
            )


def add_content_to_history(
    history: StreamHistory, content: list[dict[str, Any]]
) -> StreamHistory:
    """
    Adds content to the history.

    NOTE: Still deciding if StreamHistory should own its own content sorting logic.

    Args:
        history: StreamHistory to add the content to
        content: List of content items to add

    Returns:
        StreamHistory with the content added
    """
    for item in content:
        if item.get("type") == "text":
            history.text_responses.append(item)
        elif item.get("type") == "tool_use":
            history.tool_calls.append(item)
    return history
