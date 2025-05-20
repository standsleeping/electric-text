import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import ContentBlockType
from electric_text.providers.model_providers.openai.functions.handle_tool_start import (
    handle_tool_start,
)


def test_handle_tool_start_creates_content_block_and_adds_chunk():
    """Creates a tool call content block and adds a stream chunk to history"""
    data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "San Francisco"},
        },
    }

    raw_line = f"data: {json.dumps(data)}"

    history = StreamHistory()

    result = handle_tool_start(raw_line, data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert result.content_blocks[0].data.name == "get_weather"
    assert result.content_blocks[0].data.input == {"location": "San Francisco"}
    assert result.content_blocks[0].data.input_json_string == ""
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.TOOL_START
    assert result.chunks[0].raw_line == raw_line
    assert result.chunks[0].parsed_data == data


def test_handle_tool_start_with_specific_index():
    """Uses the provided output_index to insert the content block"""
    data = {
        "type": "response.content_part.added",
        "output_index": 1,
        "part": {
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "San Francisco"},
        },
    }
    raw_line = f"data: {json.dumps(data)}"
    history = StreamHistory()

    # Add an existing block first at index 0
    initial_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {
            "type": "tool_use",
            "name": "get_forecast",
            "input": {"location": "New York"},
        },
    }
    initial_raw_line = f"data: {json.dumps(initial_data)}"
    initial_history = handle_tool_start(initial_raw_line, initial_data, history)

    result = handle_tool_start(raw_line, data, initial_history)

    assert len(result.content_blocks) == 2
    assert result.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert result.content_blocks[0].data.name == "get_forecast"
    assert result.content_blocks[1].type == ContentBlockType.TOOL_CALL
    assert result.content_blocks[1].data.name == "get_weather"
    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.TOOL_START
    assert result.chunks[1].type == StreamChunkType.TOOL_START
