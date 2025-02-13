from models.stream_history import (
    StreamChunkType,
    StreamChunk,
    StreamHistory,
    categorize_stream_line,
)


def test_stream_chunk_empty_line():
    """Categorizes empty lines."""
    chunk = categorize_stream_line("")
    assert chunk.type == StreamChunkType.EMPTY_LINE
    assert chunk.raw_line == ""
    assert chunk.parsed_data is None
    assert chunk.content is None
    assert chunk.error is None


def test_stream_chunk_done_marker():
    """Categorizes [DONE] markers."""
    chunk = categorize_stream_line("data: [DONE]")
    assert chunk.type == StreamChunkType.STREAM_DONE
    assert chunk.raw_line == "data: [DONE]"


def test_stream_chunk_invalid_prefix():
    """Categorizes lines with invalid prefixes."""
    chunk = categorize_stream_line("invalid: {}")
    assert chunk.type == StreamChunkType.INVALID_FORMAT
    assert chunk.raw_line == "invalid: {}"


def test_stream_chunk_initial_message():
    """Categorizes initial messages with role."""
    line = 'data: {"choices":[{"delta":{"role":"assistant","content":"test"}}]}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.INITIAL_MESSAGE
    assert chunk.content == "test"
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["choices"][0]["delta"]["role"] == "assistant"


def test_stream_chunk_content():
    """Categorizes content chunks."""
    line = 'data: {"choices":[{"delta":{"content":"test content"}}]}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.CONTENT_CHUNK
    assert chunk.content == "test content"
    assert chunk.parsed_data is not None


def test_stream_chunk_completion_end():
    """Categorizes completion end markers."""
    line = 'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.COMPLETION_END
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["choices"][0]["finish_reason"] == "stop"


def test_stream_chunk_no_choices():
    """Categorizes responses without choices."""
    line = 'data: {"id":"123","object":"chat.completion.chunk"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.NO_CHOICES
    assert chunk.parsed_data is not None
    assert "choices" not in chunk.parsed_data


def test_stream_chunk_parse_error():
    """Categorizes invalid JSON."""
    line = "data: {invalid json}"
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.PARSE_ERROR
    assert chunk.error is not None
    assert "Expecting property name enclosed in double quotes" in chunk.error


def test_stream_history_accumulation():
    """Accumulates stream history."""
    history = StreamHistory()

    # Add various types of chunks
    chunks = [
        StreamChunk(StreamChunkType.INITIAL_MESSAGE, "chunk1", content="hello"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk2", content="world"),
        StreamChunk(StreamChunkType.COMPLETION_END, "chunk3"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert len(history.chunks) == 3
    assert history.chunks[0].content == "hello"
    assert history.chunks[1].content == "world"
    assert history.chunks[2].type == StreamChunkType.COMPLETION_END


def test_stream_chunk_real_openai_format():
    """Handles real OpenAI format examples."""
    # Example from the actual OpenAI response format
    line = """data: {"id":"chatcmpl-B0VY8kTSAJFk6UernyixxIbsJH3aE","object":"chat.completion.chunk","created":1739460976,"model":"gpt-4o-mini-2024-07-18","service_tier":"default","system_fingerprint":"fp_72ed7ab54c","choices":[{"index":0,"delta":{"role":"assistant","content":"","refusal":null},"logprobs":null,"finish_reason":null}]}"""
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.INITIAL_MESSAGE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["choices"][0]["delta"]["role"] == "assistant"


def test_stream_chunk_empty_content():
    """Handles chunks with empty content."""
    line = 'data: {"choices":[{"delta":{"content":""}}]}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.NO_CHOICES
    assert chunk.content is None


def test_stream_history_empty():
    """Initializes with empty history."""
    history = StreamHistory()
    assert len(history.chunks) == 0
    assert isinstance(history.chunks, list)


def test_stream_history_get_full_content():
    """Rebuilds full content from stream history."""
    history = StreamHistory()

    # Various chunk types, including non-content chunks
    chunks = [
        StreamChunk(StreamChunkType.INITIAL_MESSAGE, "chunk1", content=""),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk2", content="Hello"),
        StreamChunk(StreamChunkType.EMPTY_LINE, "chunk3"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk4", content=" world"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk5", content="!"),
        StreamChunk(StreamChunkType.COMPLETION_END, "chunk6"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert history.get_full_content() == "Hello world!"


def test_stream_history_get_full_content_empty():
    """Returns empty string when no content chunks exist."""
    history = StreamHistory()

    # Only non-content chunks
    chunks = [
        StreamChunk(StreamChunkType.INITIAL_MESSAGE, "chunk1"),
        StreamChunk(StreamChunkType.EMPTY_LINE, "chunk2"),
        StreamChunk(StreamChunkType.COMPLETION_END, "chunk3"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert history.get_full_content() == ""
