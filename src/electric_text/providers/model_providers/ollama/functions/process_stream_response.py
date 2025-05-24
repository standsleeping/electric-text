import json
from electric_text.providers.data.content_block import ContentBlock, ContentBlockType, TextData, ToolCallData
from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory


def process_stream_response(
    raw_line: str,
    history: StreamHistory,
) -> StreamHistory:
    """
    Processes a stream response line into a StreamHistory.

    This function handles individual stream response chunks from Ollama
    and adds the appropriate StreamChunk objects to the provided history.

    Args:
        raw_line: The raw line received from the stream
        history: StreamHistory to add the chunks to

    Returns:
        StreamHistory with the new chunk(s) added
    """
    chunk_data = json.loads(raw_line)

    # Extract message data
    message = chunk_data.get("message", {})
    content = message.get("content")
    tool_calls = message.get("tool_calls")

    # Process tool calls if present
    if tool_calls:
        # Process each tool call
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            func_name = function.get("name", "")
            func_args = function.get("arguments", {})

            history.add_chunk(
                StreamChunk(
                    type=StreamChunkType.FULL_TOOL_CALL,
                    raw_line=raw_line,
                    parsed_data=tool_call,
                    content=json.dumps(function),
                )
            )

            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TOOL_CALL,
                    data=ToolCallData(
                        name=func_name,
                        input=func_args,
                        input_json_string=json.dumps(func_args),
                    ),
                )
            )

    # Process content if present
    if content:
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.CONTENT_CHUNK,
                raw_line=raw_line,
                parsed_data=chunk_data,
                content=content,
            )
        )

        # Update or create content block
        # Look for existing text content block
        text_block = None
        for block in history.content_blocks:
            if block.type == ContentBlockType.TEXT:
                text_block = block
                break

        if text_block and isinstance(text_block.data, TextData):
            # Update existing text block
            text_block.data.text += content
        else:
            # Create new text block
            history.content_blocks.append(
                ContentBlock(
                    type=ContentBlockType.TEXT,
                    data=TextData(text=content),
                )
            )

    # Check for done flag
    if chunk_data.get("done", False):
        history.add_chunk(
            StreamChunk(
                type=StreamChunkType.COMPLETION_END,
                raw_line=raw_line,
                parsed_data=chunk_data,
                content=None,
            )
        )

    return history
