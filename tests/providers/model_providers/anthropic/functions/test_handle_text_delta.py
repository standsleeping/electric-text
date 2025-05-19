from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
)
from electric_text.providers.model_providers.anthropic.functions.handle_text_delta import (
    handle_text_delta,
)


def test_handle_text_delta():
    """Test handling text delta events from Anthropic."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_delta", "index": 0, "delta": {"text": "some-text"}}'
    data = {"type": "content_block_delta", "index": 0, "delta": {"text": "some-text"}}

    # Create StreamHistory with an existing content block
    history = StreamHistory()

    content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text=""),
    )

    history.content_blocks.append(content_block)

    # Call the handler
    updated_history = handle_text_delta(raw_line, data, history)

    # Verify the text was appended to the content block
    assert history.content_blocks[0].data.text == "some-text"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_DELTA
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_text_delta_with_existing_text():
    """Test handling text delta events when content already exists."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_delta", "index": 0, "delta": {"text": " continues"}}'
    data = {"type": "content_block_delta", "index": 0, "delta": {"text": " continues"}}

    # Create StreamHistory with an existing content block that already has text
    history = StreamHistory()

    content_block = ContentBlock(
        type=ContentBlockType.TEXT,
        data=TextData(text="The story"),
    )

    history.content_blocks.append(content_block)

    # Call the handler
    updated_history = handle_text_delta(raw_line, data, history)

    # Verify the text was appended to the content block
    assert history.content_blocks[0].data.text == "The story continues"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_DELTA
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_text_delta_non_zero_index():
    """Test handling text delta events for a non-zero index."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_delta", "index": 1, "delta": {"text": "Second block"}}'

    data = {
        "type": "content_block_delta",
        "index": 1,
        "delta": {"text": "Second block"},
    }

    # Create StreamHistory with multiple content blocks
    history = StreamHistory()

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="First block"),
        )
    )

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text=""),
        )
    )

    # Call the handler
    updated_history = handle_text_delta(raw_line, data, history)

    # Verify the text was appended to the correct content block
    assert history.content_blocks[0].data.text == "First block"
    assert history.content_blocks[1].data.text == "Second block"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_DELTA
