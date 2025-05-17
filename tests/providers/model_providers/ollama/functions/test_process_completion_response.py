"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory

from electric_text.providers.model_providers.ollama.functions.process_completion_response import (
    process_completion_response,
)


def test_unstructured_content():
    fresh_history = StreamHistory()
    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"LINE1\\nLINE2\\nLINE3"},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":939506375}'

    result = process_completion_response(raw_data, fresh_history)

    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[1].type == StreamChunkType.COMPLETION_END

    content = "LINE1\nLINE2\nLINE3"
    assert result.chunks[0].content == content
    assert result.chunks[1].content is None

    assert result.chunks[0].raw_line == raw_data
    assert result.chunks[1].raw_line == raw_data


def test_structured_content():
    fresh_history = StreamHistory()
    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"{\\n  \\"response_annotation\\": \\"A generic schema for describing a vehicle\\",\\n  \\"created_json_schema_definition\\": {\\n    \\"type\\": \\"object\\",\\n    \\"properties\\": {\\n      \\"weight\\": {\\n        \\"description\\": \\"The weight of the vehicle in pounds.\\",\\n        \\"type\\": [\\"integer\\", \\"null\\"],\\n        \\"default\\": null\\n      },\\n      \\"cost\\": {\\n        \\"description\\": \\"The cost of the vehicle in dollars.\\",\\n        \\"type\\": [\\"number\\", \\"null\\"],\\n        \\"default\\": null\\n      },\\n      \\"range\\": {\\n        \\"description\\": \\"The range of the vehicle in miles.\\",\\n        \\"type\\": [\\"integer\\", \\"null\\"],\\n        \\"default\\": null\\n      }\\n    }\\n  ,\\"required\\": [\\"weight\\", \\"cost\\"]\\n  ,\\"additionalProperties\\": false\\n}\\n}"},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}'

    result = process_completion_response(raw_data, fresh_history)

    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[1].type == StreamChunkType.COMPLETION_END


def test_tool_calls():
    fresh_history = StreamHistory()
    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"","tool_calls":[{"function":{"name":"getWeather","arguments":{"city":"Omaha"}}}]},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}'

    result = process_completion_response(raw_data, fresh_history)

    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.FULL_TOOL_CALL
    assert result.chunks[1].type == StreamChunkType.COMPLETION_END

    content = '{"name": "getWeather", "arguments": {"city": "Omaha"}}'
    assert result.chunks[0].content == content
    assert result.chunks[1].content is None
