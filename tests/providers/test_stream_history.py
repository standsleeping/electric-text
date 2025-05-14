from electric_text.providers.data.stream_history import (
    StreamChunkType,
    StreamChunk,
    StreamHistory,
)
from electric_text.providers.functions.categorize_stream_line import (
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


def test_stream_chunk_event_valid_type():
    """Categorizes valid event types."""
    line = "event: response.created"
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_CREATED
    assert chunk.raw_line == line


def test_stream_chunk_event_invalid_type():
    """Categorizes invalid event types."""
    line = "event: unknown_event_type"
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.INVALID_FORMAT
    assert chunk.raw_line == line


def test_stream_chunk_parse_error():
    """Categorizes invalid JSON."""
    line = "data: {invalid json}"
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.PARSE_ERROR
    assert chunk.error is not None
    assert "Expecting property name enclosed in double quotes" in chunk.error


def test_stream_response_created():
    """Categorizes response.created event."""
    line = 'data: {"type":"response.created","response":{"output":[]}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_CREATED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.created"


def test_stream_response_in_progress():
    """Categorizes response.in_progress event."""
    line = 'data: {"type":"response.in_progress","response":{"output":[]}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_IN_PROGRESS
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.in_progress"


def test_stream_response_completed():
    """Categorizes response.completed event."""
    line = 'data: {"type":"response.completed","response":{"output":[]}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_COMPLETED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.completed"


def test_stream_response_failed():
    """Categorizes response.failed event."""
    line = 'data: {"type":"response.failed","response":{"output":[]}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_FAILED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.failed"


def test_stream_response_incomplete():
    """Categorizes response.incomplete event."""
    line = 'data: {"type":"response.incomplete","response":{"output":[]}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.RESPONSE_INCOMPLETE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.incomplete"


def test_stream_output_item_added():
    """Categorizes response.output_item.added event."""
    line = 'data: {"type":"response.output_item.added","output_index":0,"item":{"id":"123","type":"text","status":"in_progress","content":"Hello","role":"assistant"}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.OUTPUT_ITEM_ADDED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.output_item.added"


def test_stream_output_item_done():
    """Categorizes response.output_item.done event."""
    line = 'data: {"type":"response.output_item.done","output_index":0,"item_id":"123"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.OUTPUT_ITEM_DONE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.output_item.done"


def test_stream_content_part_added():
    """Categorizes response.content_part.added event."""
    line = 'data: {"type":"response.content_part.added","item_id":"123","content_index":0,"content_part":{"type":"text","text":""}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.CONTENT_PART_ADDED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.content_part.added"


def test_stream_content_part_done():
    """Categorizes response.content_part.done event."""
    line = (
        'data: {"type":"response.content_part.done","item_id":"123","content_index":0}'
    )
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.CONTENT_PART_DONE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.content_part.done"


def test_stream_output_text_delta():
    """Categorizes response.output_text.delta event."""
    line = 'data: {"type":"response.output_text.delta","item_id":"123","output_index":0,"content_index":0,"delta":"Hello, world!"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.OUTPUT_TEXT_DELTA
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.output_text.delta"
    assert chunk.content == "Hello, world!"


def test_stream_output_text_done():
    """Categorizes response.output_text.done event."""
    line = 'data: {"type":"response.output_text.done","item_id":"123","output_index":0,"content_index":0}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.OUTPUT_TEXT_DONE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.output_text.done"


def test_stream_text_annotation_added():
    """Categorizes response.output_text.annotation.added event."""
    line = 'data: {"type":"response.output_text.annotation.added","item_id":"123","output_index":0,"content_index":0,"annotation":{"type":"citation","start_index":0,"end_index":10,"text":"source","metadata":{}}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.TEXT_ANNOTATION_ADDED
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.output_text.annotation.added"


def test_stream_refusal_delta():
    """Categorizes response.refusal.delta event."""
    line = 'data: {"type":"response.refusal.delta","item_id":"123","output_index":0,"delta":"I can\'t help with that"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.REFUSAL_DELTA
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.refusal.delta"


def test_stream_refusal_done():
    """Categorizes response.refusal.done event."""
    line = 'data: {"type":"response.refusal.done","item_id":"123","output_index":0}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.REFUSAL_DONE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.refusal.done"


def test_stream_function_call_arguments_delta():
    """Categorizes response.function_call_arguments.delta event."""
    line = 'data: {"type":"response.function_call_arguments.delta","item_id":"123","output_index":0,"delta":"{\\"name\\":\\"func\\"}"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.function_call_arguments.delta"


def test_stream_function_call_arguments_done():
    """Categorizes response.function_call_arguments.done event."""
    line = 'data: {"type":"response.function_call_arguments.done","item_id":"123","output_index":0}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
    assert chunk.parsed_data is not None
    assert chunk.parsed_data["type"] == "response.function_call_arguments.done"


def test_stream_file_search_call_events():
    """Categorizes file search call events."""
    events = [
        'data: {"type":"response.file_search_call.in_progress","item_id":"123"}',
        'data: {"type":"response.file_search_call.searching","item_id":"123"}',
        'data: {"type":"response.file_search_call.completed","item_id":"123"}',
    ]

    expected_types = [
        StreamChunkType.FILE_SEARCH_CALL_IN_PROGRESS,
        StreamChunkType.FILE_SEARCH_CALL_SEARCHING,
        StreamChunkType.FILE_SEARCH_CALL_COMPLETED,
    ]

    for i, line in enumerate(events):
        chunk = categorize_stream_line(line)
        assert chunk.type == expected_types[i]
        assert chunk.parsed_data is not None


def test_stream_web_search_call_events():
    """Categorizes web search call events."""
    events = [
        'data: {"type":"response.web_search_call.in_progress","item_id":"123"}',
        'data: {"type":"response.web_search_call.searching","item_id":"123"}',
        'data: {"type":"response.web_search_call.completed","item_id":"123"}',
    ]

    expected_types = [
        StreamChunkType.WEB_SEARCH_CALL_IN_PROGRESS,
        StreamChunkType.WEB_SEARCH_CALL_SEARCHING,
        StreamChunkType.WEB_SEARCH_CALL_COMPLETED,
    ]

    for i, line in enumerate(events):
        chunk = categorize_stream_line(line)
        assert chunk.type == expected_types[i]
        assert chunk.parsed_data is not None


def test_stream_reasoning_summary_events():
    """Categorizes reasoning summary events."""
    events = [
        'data: {"type":"response.reasoning_summary_part.added","item_id":"123"}',
        'data: {"type":"response.reasoning_summary_part.done","item_id":"123"}',
        'data: {"type":"response.reasoning_summary_text.delta","item_id":"123","delta":"Thinking..."}',
        'data: {"type":"response.reasoning_summary_text.done","item_id":"123"}',
    ]

    expected_types = [
        StreamChunkType.REASONING_SUMMARY_PART_ADDED,
        StreamChunkType.REASONING_SUMMARY_PART_DONE,
        StreamChunkType.REASONING_SUMMARY_TEXT_DELTA,
        StreamChunkType.REASONING_SUMMARY_TEXT_DONE,
    ]

    for i, line in enumerate(events):
        chunk = categorize_stream_line(line)
        assert chunk.type == expected_types[i]
        assert chunk.parsed_data is not None


def test_stream_unknown_event_type():
    """Categorizes unknown event types."""
    line = 'data: {"type":"unknown.event.type","data":{}}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.INVALID_FORMAT
    assert chunk.raw_line == line


def test_stream_missing_type_field():
    """Handles data without type field."""
    line = 'data: {"id":"123","object":"chat.completion.chunk"}'
    chunk = categorize_stream_line(line)
    assert chunk.type == StreamChunkType.INVALID_FORMAT
    assert chunk.raw_line == line


def test_stream_history_accumulation():
    """Accumulates stream history."""
    history = StreamHistory()

    # Add various types of chunks
    chunks = [
        StreamChunk(StreamChunkType.OUTPUT_TEXT_DELTA, "chunk1", content="hello"),
        StreamChunk(StreamChunkType.OUTPUT_TEXT_DELTA, "chunk2", content=" world"),
        StreamChunk(StreamChunkType.OUTPUT_TEXT_DONE, "chunk3"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert len(history.chunks) == 3
    assert history.chunks[0].content == "hello"
    assert history.chunks[1].content == " world"
    assert history.chunks[2].type == StreamChunkType.OUTPUT_TEXT_DONE


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
        StreamChunk(StreamChunkType.RESPONSE_CREATED, "chunk1"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk2", content="Hello"),
        StreamChunk(StreamChunkType.EMPTY_LINE, "chunk3"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk4", content=" world"),
        StreamChunk(StreamChunkType.CONTENT_CHUNK, "chunk5", content="!"),
        StreamChunk(StreamChunkType.OUTPUT_TEXT_DONE, "chunk6"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert history.get_full_content() == "Hello world!"


def test_stream_history_get_full_content_empty():
    """Returns empty string when no content chunks exist."""
    history = StreamHistory()

    # Only non-content chunks
    chunks = [
        StreamChunk(StreamChunkType.RESPONSE_CREATED, "chunk1"),
        StreamChunk(StreamChunkType.EMPTY_LINE, "chunk2"),
        StreamChunk(StreamChunkType.OUTPUT_TEXT_DONE, "chunk3"),
    ]

    for chunk in chunks:
        history.add_chunk(chunk)

    assert history.get_full_content() == ""


def test_stream_history_from_complete_response():
    """Creates StreamHistory from complete response."""
    response_data = {
        "id": "123",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a complete response.",
                }
            }
        ],
    }

    history = StreamHistory.from_complete_response(response_data)
    assert len(history.chunks) == 1
    assert history.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
    assert history.chunks[0].content == "This is a complete response."
    assert history.get_full_content() == "This is a complete response."


def test_stream_history_from_complete_response_no_choices():
    """Handles complete response with no choices."""
    response_data = {
        "id": "123",
    }

    history = StreamHistory.from_complete_response(response_data)
    assert len(history.chunks) == 1
    assert history.chunks[0].type == StreamChunkType.NO_CHOICES
    assert history.get_full_content() == ""
