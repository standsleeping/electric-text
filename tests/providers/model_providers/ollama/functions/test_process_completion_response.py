"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from typing import Any

from electric_text.providers.data.content_block import ContentBlock, ContentBlockType
from electric_text.providers.data.stream_history import StreamHistory

from electric_text.providers.model_providers.ollama.functions.process_completion_response import (
    process_completion_response,
)


def test_unstructured_content():
    history: StreamHistory = StreamHistory()

    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"LINE1\\nLINE2\\nLINE3"},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":939506375}'

    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = "LINE1\nLINE2\nLINE3"

    actual_text: str = first_block.data.text

    assert actual_text == expected_text


def test_structured_content():
    history: StreamHistory = StreamHistory()

    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"{\\n  \\"response_annotation\\": \\"A generic schema for describing a vehicle\\",\\n  \\"created_json_schema_definition\\": {\\n    \\"type\\": \\"object\\",\\n    \\"properties\\": {\\n      \\"weight\\": {\\n        \\"description\\": \\"The weight of the vehicle in pounds.\\",\\n        \\"type\\": [\\"integer\\", \\"null\\"],\\n        \\"default\\": null\\n      },\\n      \\"cost\\": {\\n        \\"description\\": \\"The cost of the vehicle in dollars.\\",\\n        \\"type\\": [\\"number\\", \\"null\\"],\\n        \\"default\\": null\\n      },\\n      \\"range\\": {\\n        \\"description\\": \\"The range of the vehicle in miles.\\",\\n        \\"type\\": [\\"integer\\", \\"null\\"],\\n        \\"default\\": null\\n      }\\n    }\\n  ,\\"required\\": [\\"weight\\", \\"cost\\"]\\n  ,\\"additionalProperties\\": false\\n}\\n}"},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}'

    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = '{\n  "response_annotation": "A generic schema for describing a vehicle",\n  "created_json_schema_definition": {\n    "type": "object",\n    "properties": {\n      "weight": {\n        "description": "The weight of the vehicle in pounds.",\n        "type": ["integer", "null"],\n        "default": null\n      },\n      "cost": {\n        "description": "The cost of the vehicle in dollars.",\n        "type": ["number", "null"],\n        "default": null\n      },\n      "range": {\n        "description": "The range of the vehicle in miles.",\n        "type": ["integer", "null"],\n        "default": null\n      }\n    }\n  ,"required": ["weight", "cost"]\n  ,"additionalProperties": false\n}\n}'

    actual_text: str = first_block.data.text

    assert actual_text == expected_text


def test_tool_calls():
    history: StreamHistory = StreamHistory()

    raw_data = '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"","tool_calls":[{"function":{"name":"getWeather","arguments":{"city":"Omaha"}}}]},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}'

    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TOOL_CALL

    expected_name: str = "getWeather"

    actual_name: str = first_block.data.name

    assert actual_name == expected_name

    expected_input_json_string: str = '{"city": "Omaha"}'

    actual_input_json_string: str = first_block.data.input_json_string

    assert actual_input_json_string == expected_input_json_string

    expected_input: dict[str, Any] = {"city": "Omaha"}

    actual_input: dict[str, Any] = first_block.data.input

    assert actual_input == expected_input
