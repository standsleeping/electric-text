import json
from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    ToolCallData,
    TextData,
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
    output = data.get("output", [])

    for output_item in output:
        output_type = output_item.get("type", "")

        if output_type == "message":
            # Handle message format with content array
            content = output_item.get("content", [])
            for content_item in content:
                content_type = content_item.get("type", "")

                if content_type == "output_text":
                    text_content = content_item.get("text", "")
                    history.content_blocks.append(
                        ContentBlock(
                            type=ContentBlockType.TEXT,
                            data=TextData(text=text_content),
                        )
                    )

                    history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.CONTENT_CHUNK,
                            raw_line=line,
                            parsed_data=data,
                            content=text_content,
                        )
                    )

                elif content_type == "tool_use":
                    tool_name = content_item.get("name", "")
                    tool_input = content_item.get("input", {})
                    tool_input_str = json.dumps(tool_input)

                    history.content_blocks.append(
                        ContentBlock(
                            type=ContentBlockType.TOOL_CALL,
                            data=ToolCallData(
                                name=tool_name,
                                input=tool_input,
                                input_json_string=tool_input_str,
                            ),
                        )
                    )

                    history.add_chunk(
                        StreamChunk(
                            type=StreamChunkType.TOOL_START,
                            raw_line=line,
                            parsed_data=data,
                            content="",
                        )
                    )

        elif output_type == "function_call":
            # Handle function_call format with direct function data
            tool_name = output_item.get("name", "")
            arguments_str = output_item.get("arguments", "{}")
            tool_input = json.loads(arguments_str)

            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TOOL_CALL,
                    data=ToolCallData(
                        name=tool_name,
                        input=tool_input,
                        input_json_string=arguments_str,
                    ),
                )
            )

            history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.TOOL_START,
                    raw_line=line,
                    parsed_data=data,
                    content="",
                )
            )

    return history
