import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    ToolCallData,
    TextData,
)
from electric_text.providers.model_providers.anthropic.functions.handle_tool_start import (
    handle_tool_start,
)


def test_handle_tool_start():
    """Test handling tool start events from Anthropic."""
    # Set up initial test data
    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "San Francisco", "unit": "celsius"},
        },
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create empty StreamHistory
    history = StreamHistory()

    # Call the handler
    updated_history = handle_tool_start(raw_line, data, history)

    # Verify the content block was created with the right tool call data
    assert len(history.content_blocks) == 1
    assert history.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert history.content_blocks[0].data.name == "get_weather"
    assert history.content_blocks[0].data.input == {
        "location": "San Francisco",
        "unit": "celsius",
    }

    assert history.content_blocks[0].data.input_json_string == ""

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_START
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_tool_start_with_existing_blocks():
    """Test handling tool start events when blocks already exist."""
    # Set up initial test data
    data = {
        "type": "content_block_start",
        "index": 1,
        "content_block": {
            "type": "tool_use",
            "name": "get_forecast",
            "input": {"location": "New York", "days": 5},
        },
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create StreamHistory with an existing content block
    history = StreamHistory()

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="Here's the weather forecast:"),
        )
    )

    # Call the handler
    updated_history = handle_tool_start(raw_line, data, history)

    # Verify the content block was inserted at the right index
    assert len(history.content_blocks) == 2
    assert history.content_blocks[0].type == ContentBlockType.TEXT
    assert history.content_blocks[1].type == ContentBlockType.TOOL_CALL
    assert history.content_blocks[1].data.name == "get_forecast"
    assert history.content_blocks[1].data.input == {"location": "New York", "days": 5}

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_START


def test_handle_tool_start_insert_at_beginning():
    """Test handling tool start events with insertion at index 0."""
    # Set up initial test data
    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {
            "type": "tool_use",
            "name": "search_database",
            "input": {"query": "climate data"},
        },
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create StreamHistory with existing content blocks
    history = StreamHistory()

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TOOL_CALL,
            data=ToolCallData(
                name="get_weather",
                input={"location": "London"},
                input_json_string="",
            ),
        )
    )

    # Call the handler
    updated_history = handle_tool_start(raw_line, data, history)

    # Verify the content block was inserted at the beginning
    assert len(history.content_blocks) == 2
    assert history.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert history.content_blocks[0].data.name == "search_database"
    assert history.content_blocks[0].data.input == {"query": "climate data"}
    assert history.content_blocks[1].data.name == "get_weather"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_START


def test_handle_tool_start_empty_input():
    """Test handling tool start events with empty input."""
    # Set up initial test data
    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "tool_use", "name": "get_current_time", "input": {}},
    }

    raw_line = f"data: {json.dumps(data)}"

    # Create empty StreamHistory
    history = StreamHistory()

    # Call the handler
    updated_history = handle_tool_start(raw_line, data, history)

    # Verify the content block was created with empty input
    assert len(history.content_blocks) == 1
    assert history.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert history.content_blocks[0].data.name == "get_current_time"
    assert history.content_blocks[0].data.input == {}
    assert history.content_blocks[0].data.input_json_string == ""

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TOOL_START
