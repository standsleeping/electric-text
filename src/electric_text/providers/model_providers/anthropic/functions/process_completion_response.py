import json
from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
    ToolCallData,
)


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
                    type=StreamChunkType.FULL_TOOL_CALL,
                    raw_line=line,
                    parsed_data=data,
                )
            )
        case "end_turn":
            raw_content: str = data["content"][0]["text"]

            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TEXT,
                    data=TextData(text=raw_content),
                )
            )

            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.FULL_TEXT,
                    raw_line=line,
                    parsed_data=data,
                )
            )

        case _:
            return history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.UNHANDLED_EVENT,
                    raw_line=line,
                    parsed_data=data,
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
            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TEXT,
                    data=TextData(text=item.get("text", "")),
                )
            )
        elif item.get("type") == "tool_use":
            name = item.get("name", "")
            input = item.get("input", {})
            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TOOL_CALL,
                    data=ToolCallData(
                        name=name,
                        input=input,
                        input_json_string=json.dumps(input),
                    ),
                )
            )

    return history
