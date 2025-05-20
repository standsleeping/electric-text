import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import ContentBlockType
from electric_text.providers.model_providers.openai.functions.handle_tool_delta import (
    handle_tool_delta,
)
from electric_text.providers.model_providers.openai.functions.handle_tool_start import (
    handle_tool_start,
)


def test_handle_tool_delta_updates_content_block():
    """Updates the tool input JSON string in a content block and adds a stream chunk to history"""
    # First, create a tool call block
    start_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "Omaha"},
        },
    }

    start_raw_line = f"data: {json.dumps(start_data)}"

    history = StreamHistory()

    history = handle_tool_start(start_raw_line, start_data, history)

    # Now prepare a delta
    delta_data = {
        "type": "response.tool_input.delta",
        "output_index": 0,
        "delta": '{"location":',
    }

    delta_raw_line = f"data: {json.dumps(delta_data)}"

    result = handle_tool_delta(delta_raw_line, delta_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert result.content_blocks[0].data.name == "get_weather"
    assert result.content_blocks[0].data.input == {"location": "Omaha"}
    assert result.content_blocks[0].data.input_json_string == '{"location":'
    assert len(result.chunks) == 2  # One from start, one from delta
    assert result.chunks[0].type == StreamChunkType.TOOL_START
    assert result.chunks[1].type == StreamChunkType.TOOL_DELTA
    assert result.chunks[1].raw_line == delta_raw_line
    assert result.chunks[1].parsed_data == delta_data


def test_handle_tool_delta_with_multiple_updates():
    """Updates the tool input JSON string with multiple deltas"""
    # First, create a tool call block
    start_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {
            "type": "tool_use",
            "name": "get_weather",
            "input": {"location": "Omaha"},
        },
    }

    start_raw_line = f"data: {json.dumps(start_data)}"

    history = StreamHistory()

    history = handle_tool_start(start_raw_line, start_data, history)

    # Now prepare deltas
    delta1_data = {
        "type": "response.tool_input.delta",
        "output_index": 0,
        "delta": '{"location":',
    }

    delta1_raw_line = f"data: {json.dumps(delta1_data)}"

    history = handle_tool_delta(delta1_raw_line, delta1_data, history)

    delta2_data = {
        "type": "response.tool_input.delta",
        "output_index": 0,
        "delta": ' "Omaha"}',
    }

    delta2_raw_line = f"data: {json.dumps(delta2_data)}"

    result = handle_tool_delta(delta2_raw_line, delta2_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TOOL_CALL
    assert result.content_blocks[0].data.name == "get_weather"
    assert result.content_blocks[0].data.input == {"location": "Omaha"}
    assert result.content_blocks[0].data.input_json_string == '{"location": "Omaha"}'
    assert len(result.chunks) == 3  # One from start, two from deltas
    assert result.chunks[0].type == StreamChunkType.TOOL_START
    assert result.chunks[1].type == StreamChunkType.TOOL_DELTA
    assert result.chunks[2].type == StreamChunkType.TOOL_DELTA
