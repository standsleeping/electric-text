import json
from typing import Any
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import ContentBlockType, ToolCallData


def handle_function_call_arguments_done(
    raw_line: str,
    data: dict[str, Any],
    history: StreamHistory,
) -> StreamHistory:
    """
    Handle completion of function call arguments in OpenAI stream responses.

    This function finalizes the function call arguments by parsing the complete JSON
    and updating the input field. It is triggered when a response.function_call_arguments.done
    event is received from OpenAI.

    Args:
        raw_line: The raw line received from the stream
        data: The parsed JSON data from the stream
        history: The current StreamHistory

    Returns:
        Updated StreamHistory with the updated content block and new chunk
    """
    arguments = data.get("arguments", "")
    output_index = data.get("output_index", 0)

    # Get the content block at the specified index and finalize its input
    content_block = history.content_blocks[output_index]
    if content_block.type == ContentBlockType.TOOL_CALL:
        assert isinstance(content_block.data, ToolCallData)
        # Parse the complete arguments JSON and update the input field
        try:
            content_block.data.input = json.loads(arguments)
            # Also ensure the input_json_string matches the final arguments
            content_block.data.input_json_string = arguments
        except json.JSONDecodeError:
            # If parsing fails, keep the input as empty dict but preserve the string
            content_block.data.input = {}
            content_block.data.input_json_string = arguments

    # Add a chunk to record this completion
    return history.add_chunk(
        StreamChunk(
            type=StreamChunkType.TOOL_DELTA,  # or we could add a TOOL_DONE type
            raw_line=raw_line,
            parsed_data=data,
            content="",
        )
    )
