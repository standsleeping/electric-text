"""
A provider's test_process_stream_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.model_providers.anthropic.functions.process_stream_response import (
    process_stream_response,
)


def test_unstructured_content():
    history: StreamHistory = StreamHistory()
    chunks: list[str] = [
        "event: message_start",
        'data: {"type":"message_start","message":{"id":"msg_011H6dxt5XrHnyhEi6JBv57P","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":131,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":5}}}',
        "",
        "event: content_block_start",
        'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}',
        "",
        "event: ping",
        'data: {"type": "ping"}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Petrichor rises"}}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"  \\nCorn"}}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" unfurls to catch"}}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" droplets  \\nEarth"}}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" speaks to lightning"}}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_stop","index":0}',
        "",
        "event: message_delta",
        'data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":25}}',
        "",
        "event: message_stop",
        'data: {"type":"message_stop"}',
        "",
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    assert len(history.chunks) == 10


def test_structured_content():
    pass


def test_tool_calls():
    pass
