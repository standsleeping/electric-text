from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.content_block import (
    ContentBlock,
    ContentBlockType,
    TextData,
)
from electric_text.providers.model_providers.anthropic.functions.handle_text_start import (
    handle_text_start,
)


def test_handle_text_start():
    """Test handling text start events from Anthropic."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": "Initial text"}}'

    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": "Initial text"},
    }

    # Create empty StreamHistory
    history = StreamHistory()

    # Call the handler
    updated_history = handle_text_start(raw_line, data, history)

    # Verify the content block was created with the right text
    assert len(history.content_blocks) == 1
    assert history.content_blocks[0].type == ContentBlockType.TEXT
    assert history.content_blocks[0].data.text == "Initial text"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_START
    assert updated_history.chunks[0].raw_line == raw_line
    assert updated_history.chunks[0].parsed_data == data


def test_handle_text_start_with_existing_blocks():
    """Test handling text start events when blocks already exist."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": "Second block"}}'

    data = {
        "type": "content_block_start",
        "index": 1,
        "content_block": {"type": "text", "text": "Second block"},
    }

    # Create StreamHistory with an existing content block
    history = StreamHistory()

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="First block"),
        )
    )

    # Call the handler
    updated_history = handle_text_start(raw_line, data, history)

    # Verify the content block was inserted at the right index
    assert len(history.content_blocks) == 2
    assert history.content_blocks[0].data.text == "First block"
    assert history.content_blocks[1].data.text == "Second block"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_START


def test_handle_text_start_insert_at_beginning():
    """Test handling text start events with insertion at index 0."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": "New first block"}}'

    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": "New first block"},
    }

    # Create StreamHistory with existing content blocks
    history = StreamHistory()

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="Original first block"),
        )
    )

    history.content_blocks.append(
        ContentBlock(
            type=ContentBlockType.TEXT,
            data=TextData(text="Original second block"),
        )
    )

    # Call the handler
    updated_history = handle_text_start(raw_line, data, history)

    # Verify the content block was inserted at the beginning
    assert len(history.content_blocks) == 3
    assert history.content_blocks[0].data.text == "New first block"
    assert history.content_blocks[1].data.text == "Original first block"
    assert history.content_blocks[2].data.text == "Original second block"

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_START


def test_handle_text_start_empty_text():
    """Test handling text start events with empty text content."""
    # Set up initial test data
    raw_line = 'data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}'

    data = {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""},
    }

    # Create empty StreamHistory
    history = StreamHistory()

    # Call the handler
    updated_history = handle_text_start(raw_line, data, history)

    # Verify the content block was created with empty text
    assert len(history.content_blocks) == 1
    assert history.content_blocks[0].type == ContentBlockType.TEXT
    assert history.content_blocks[0].data.text == ""

    # Verify a StreamChunk was added to the history
    assert len(updated_history.chunks) == 1
    assert updated_history.chunks[0].type == StreamChunkType.TEXT_START
