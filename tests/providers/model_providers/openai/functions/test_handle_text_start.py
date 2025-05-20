import json
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import ContentBlockType
from electric_text.providers.model_providers.openai.functions.handle_text_start import (
    handle_text_start,
)


def test_handle_text_start_creates_content_block_and_adds_chunk():
    """Creates a content block and adds a stream chunk to history"""
    # Arrange
    data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {"type": "output_text", "text": ""},
    }

    raw_line = f"data: {json.dumps(data)}"

    history = StreamHistory()

    # Act
    result = handle_text_start(raw_line, data, history)

    # Assert
    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[0].data.text == ""
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.TEXT_START
    assert result.chunks[0].raw_line == raw_line
    assert result.chunks[0].parsed_data == data


def test_handle_text_start_with_specific_index():
    """Uses the provided output_index to insert the content block"""
    # Arrange
    data = {
        "type": "response.content_part.added",
        "output_index": 1,
        "part": {"type": "output_text", "text": ""},
    }

    raw_line = f"data: {json.dumps(data)}"

    history = StreamHistory()

    # Add an existing block first at index 0
    initial_data = {
        "type": "response.content_part.added",
        "output_index": 0,
        "part": {"type": "output_text", "text": ""},
    }

    initial_raw_line = f"data: {json.dumps(initial_data)}"

    initial_history = handle_text_start(initial_raw_line, initial_data, history)

    # Act
    result = handle_text_start(raw_line, data, initial_history)

    # Assert
    assert len(result.content_blocks) == 2
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[1].type == ContentBlockType.TEXT
    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.TEXT_START
    assert result.chunks[1].type == StreamChunkType.TEXT_START
