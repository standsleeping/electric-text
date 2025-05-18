"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory

from electric_text.providers.model_providers.anthropic.functions.process_completion_response import (
    process_completion_response,
)

def test_unstructured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{"id":"msg_01HfDWUPQJka4rnZKHhjkgGi","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[{"type":"text","text":"LINE1\\nLINE2\\nLINE3"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":99,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":99}}'
    result: StreamHistory = process_completion_response(raw_data, history)
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[0].content == "LINE1\nLINE2\nLINE3"

def test_structured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{"id": "msg_01PfkFF5f3YRQsaHRX3GxBB6", "type": "message", "role": "assistant", "model": "claude-3-7-sonnet-20250219", "content": [{"type": "text", "text": "\\n  \\"type\\": \\"object\\",\\n  \\"description\\": \\"Information about a vehicle\\",\\n  \\"properties\\": {\\n    \\"weight\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The weight of the vehicle in pounds\\"\\n    },\\n    \\"cost\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The price of the vehicle in dollars\\"\\n    },\\n    \\"range\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The maximum driving distance of the vehicle in miles\\"\\n    }\\n  },\\n  \\"required\\": [\\"weight\\", \\"cost\\", \\"range\\"]\\n}"}], "stop_reason": "end_turn", "stop_sequence": null, "usage": {"input_tokens": 99, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 99}}'
    result: StreamHistory = process_completion_response(raw_data, history)
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK

def test_tool_calls():
    # TODO: Implement this test
    pass