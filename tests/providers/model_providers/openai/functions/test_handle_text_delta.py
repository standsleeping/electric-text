import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import ContentBlockType
from electric_text.providers.model_providers.openai.functions.handle_text_delta import (
    handle_text_delta,
)
from electric_text.providers.model_providers.openai.functions.handle_text_start import (
    handle_text_start,
)


def test_handle_text_delta_updates_content_block():
    """Updates the text in a content block and adds a stream chunk to history"""

    # First, create a text block
    start_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {"type": "output_text", "text": ""},
    }

    start_raw_line = f"data: {json.dumps(start_data)}"

    history = StreamHistory()

    history = handle_text_start(start_raw_line, start_data, history)

    # Now prepare a delta
    delta_data = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "delta": "Hello",
    }

    delta_raw_line = f"data: {json.dumps(delta_data)}"

    result = handle_text_delta(delta_raw_line, delta_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[0].data.text == "Hello"
    assert len(result.chunks) == 2  # One from start, one from delta
    assert result.chunks[0].type == StreamChunkType.TEXT_START
    assert result.chunks[1].type == StreamChunkType.TEXT_DELTA
    assert result.chunks[1].raw_line == delta_raw_line
    assert result.chunks[1].parsed_data == delta_data


def test_handle_text_delta_with_multiple_updates():
    """Updates the text content with multiple deltas"""
    # First, create a text block
    start_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {"type": "output_text", "text": ""},
    }

    start_raw_line = f"data: {json.dumps(start_data)}"

    history = StreamHistory()

    history = handle_text_start(start_raw_line, start_data, history)

    # Now prepare deltas
    delta1_data = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "delta": "Hello",
    }

    delta1_raw_line = f"data: {json.dumps(delta1_data)}"

    history = handle_text_delta(delta1_raw_line, delta1_data, history)

    delta2_data = {
        "type": "response.output_text.delta",
        "output_index": 0,
        "delta": ", world",
    }

    delta2_raw_line = f"data: {json.dumps(delta2_data)}"

    result = handle_text_delta(delta2_raw_line, delta2_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[0].data.text == "Hello, world"
    assert len(result.chunks) == 3  # One from start, two from deltas
    assert result.chunks[0].type == StreamChunkType.TEXT_START
    assert result.chunks[1].type == StreamChunkType.TEXT_DELTA
    assert result.chunks[2].type == StreamChunkType.TEXT_DELTA
