import json
from typing import List
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)


def process_tool_calls(response: ModelResponse) -> List[StreamChunk]:
    """
    Processes tool calls from a ModelResponse into StreamChunks.

    Args:
        response: ModelResponse containing tool calls to process

    Returns:
        List of StreamChunks containing the processed tool calls
    """
    if not response.message.tool_calls:
        return []

    chunks = []

    # Process each tool call
    for tool_call in response.message.tool_calls:
        chunks.append(
            StreamChunk(
                type=StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA,
                raw_line=json.dumps(tool_call.function),
                parsed_data=tool_call.function,
                content=json.dumps(tool_call.function),
            )
        )

    # Add completion of function calls
    chunks.append(
        StreamChunk(
            type=StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE,
            raw_line=json.dumps([tc.function for tc in response.message.tool_calls]),
            parsed_data={
                "tool_calls": json.dumps(
                    [tc.function for tc in response.message.tool_calls]
                )
            },
            content="",
        )
    )

    return chunks
