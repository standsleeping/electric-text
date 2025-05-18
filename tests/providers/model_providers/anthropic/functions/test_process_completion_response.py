"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from typing import Any

from electric_text.providers.data.content_block import ContentBlock, ContentBlockType
from electric_text.providers.data.stream_history import StreamHistory

from electric_text.providers.model_providers.anthropic.functions.process_completion_response import (
    process_completion_response,
)


def test_unstructured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{"id":"msg_01HfDWUPQJka4rnZKHhjkgGi","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[{"type":"text","text":"LINE1\\nLINE2\\nLINE3"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":99,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":99}}'
    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = "LINE1\nLINE2\nLINE3"

    actual_text: str = first_block.data.text

    assert actual_text == expected_text


def test_structured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{"id": "msg_01PfkFF5f3YRQsaHRX3GxBB6", "type": "message", "role": "assistant", "model": "claude-3-7-sonnet-20250219", "content": [{"type": "text", "text": "\\n  \\"type\\": \\"object\\",\\n  \\"description\\": \\"Information about a vehicle\\",\\n  \\"properties\\": {\\n    \\"weight\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The weight of the vehicle in pounds\\"\\n    },\\n    \\"cost\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The price of the vehicle in dollars\\"\\n    },\\n    \\"range\\": {\\n      \\"type\\": \\"number\\",\\n      \\"description\\": \\"The maximum driving distance of the vehicle in miles\\"\\n    }\\n  },\\n  \\"required\\": [\\"weight\\", \\"cost\\", \\"range\\"]\\n}"}], "stop_reason": "end_turn", "stop_sequence": null, "usage": {"input_tokens": 99, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 99}}'
    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = '\n  "type": "object",\n  "description": "Information about a vehicle",\n  "properties": {\n    "weight": {\n      "type": "number",\n      "description": "The weight of the vehicle in pounds"\n    },\n    "cost": {\n      "type": "number",\n      "description": "The price of the vehicle in dollars"\n    },\n    "range": {\n      "type": "number",\n      "description": "The maximum driving distance of the vehicle in miles"\n    }\n  },\n  "required": ["weight", "cost", "range"]\n}'

    actual_text: str = first_block.data.text

    assert actual_text == expected_text


def test_tool_calls():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{"id":"msg_01Xr8iUvUY3DcGv2Kb3msXbD","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[{"type":"text","text":"I\'d be happy to check the current weather in Omaha for you. Let me get that information."},{"type":"tool_use","id":"toolu_01SDkdmBb7seNewqWJPnBDiR","name":"get_current_weather","input":{"location":"Omaha, NE"}}],"stop_reason":"tool_use","stop_sequence":null,"usage":{"input_tokens":544,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":83}}'
    result: StreamHistory = process_completion_response(raw_data, history)

    first_block: ContentBlock = result.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = "I'd be happy to check the current weather in Omaha for you. Let me get that information."

    actual_text: str = first_block.data.text

    assert actual_text == expected_text

    second_block: ContentBlock = result.content_blocks[1]

    assert second_block.type == ContentBlockType.TOOL_CALL

    expected_name: str = "get_current_weather"

    actual_name: str = second_block.data.name

    assert actual_name == expected_name

    expected_input_json_string: str = '{"location": "Omaha, NE"}'

    actual_input_json_string: str = second_block.data.input_json_string

    assert actual_input_json_string == expected_input_json_string

    expected_input: dict[str, Any] = {"location": "Omaha, NE"}

    actual_input: dict[str, Any] = second_block.data.input

    assert actual_input == expected_input
