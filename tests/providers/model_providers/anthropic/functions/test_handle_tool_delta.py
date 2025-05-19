import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    ToolCallData,
    TextData,
)
from electric_text.providers.model_providers.anthropic.functions.handle_tool_delta import (
    handle_tool_delta,
)


def test_handle_tool_delta():
    """Test handling tool delta events from Anthropic."""
    # Set up initial test data
    data = {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"partial_json": '{"location":'},
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create StreamHistory with an existing tool call content block
    history = StreamHistory()

    content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name="get_weather",
            input={},
            input_json_string="",
        ),
    )

    history.content_blocks.append(content_block)

    # Call the handler
    updated_history = handle_tool_delta(raw_line, data, history)

    # Verify the partial JSON was appended to the tool call
    assert history.content_blocks[0].data.input_json_string == '{"location":'

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_DELTA
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_tool_delta_with_existing_json():
    """Test handling tool delta events when partial JSON already exists."""
    # Set up initial test data
    data = {
        "type": "content_block_delta",
        "index": 0,
        "delta": {"partial_json": ' "New York"}'},
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create StreamHistory with an existing tool call that already has partial JSON
    history = StreamHistory()

    content_block = ContentBlock(
        type=ContentBlockType.TOOL_CALL,
        data=ToolCallData(
            name="get_weather",
            input={},
            input_json_string='{"location":',
        ),
    )

    history.content_blocks.append(content_block)

    # Call the handler
    updated_history = handle_tool_delta(raw_line, data, history)

    # Verify the partial JSON was appended correctly
    assert (
        history.content_blocks[0].data.input_json_string == '{"location": "New York"}'
    )

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_DELTA
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_tool_delta_non_zero_index():
    """Test handling tool delta events for a non-zero index."""
    # Set up initial test data
    data = {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"partial_json": '{"unit": "celsius"}'},
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create StreamHistory with multiple content blocks
    history = StreamHistory()

    # First block - a text block
    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="Text content"),
        )
    )

    # Second block - a tool call
    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TOOL_CALL,
            data=ToolCallData(
                name="get_weather",
                input={},
                input_json_string="",
            ),
        )
    )

    # Call the handler
    updated_history = handle_tool_delta(raw_line, data, history)

    # Verify the partial JSON was appended to the correct content block
    assert history.content_blocks[1].data.input_json_string == '{"unit": "celsius"}'

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_DELTA
