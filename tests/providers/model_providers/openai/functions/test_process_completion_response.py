"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.content_block import ContentBlockType
from electric_text.providers.model_providers.openai.functions.process_completion_response import (
    process_completion_response,
)


def test_unstructured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{\n  "id": "resp_68296e0303e88191bb97635af8f14f150bb08925da38f793",\n  "object": "response",\n  "created_at": 1747545603,\n  "status": "completed",\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-mini-2024-07-18",\n  "output": [\n    {\n      "id": "msg_68296e03592c8191b24da99b0fdada0a0bb08925da38f793",\n      "type": "message",\n      "status": "completed",\n      "content": [\n        {\n          "type": "output_text",\n          "annotations": [],\n          "text": "dusty asphalt wakes\\u2014  \\ngreen shoots sip the heavy air,  \\nearth\'s breath, warm and sweet."\n        }\n      ],\n      "role": "assistant"\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "service_tier": "default",\n  "store": true,\n  "temperature": 1.0,\n  "text": {\n    "format": {\n      "type": "text"\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [],\n  "top_p": 1.0,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 112,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 23,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 135\n  },\n  "user": null,\n  "metadata": {}\n}'
    result: StreamHistory = process_completion_response(raw_data, history)

    expected_text = "dusty asphalt wakes—  \ngreen shoots sip the heavy air,  \nearth's breath, warm and sweet."

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[0].data.text == expected_text


def test_structured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{\n  "id": "resp_68296f8d9de481918035c4cd6fd7c86b0226c27a0a5b5572",\n  "object": "response",\n  "created_at": 1747545997,\n  "status": "completed",\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-mini-2024-07-18",\n  "output": [\n    {\n      "id": "msg_68296f8df07c8191993b14962d4db7df0226c27a0a5b5572",\n      "type": "message",\n      "status": "completed",\n      "content": [\n        {\n          "type": "output_text",\n          "annotations": [],\n          "text": "{\\"description\\":\\"Attributes defining a car\'s specifications.\\",\\"properties\\":{\\"weight\\":{\\"type\\":\\"integer\\",\\"description\\":\\"The weight of the car in pounds\\"},\\"cost\\":{\\"type\\":\\"number\\",\\"description\\":\\"The cost of the car in dollars\\"},\\"range\\":{\\"type\\":\\"integer\\",\\"description\\":\\"The range of the car in miles\\"}},\\"type\\":\\"object\\"}"\n        }\n      ],\n      "role": "assistant"\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "service_tier": "default",\n  "store": true,\n  "temperature": 1.0,\n  "text": {\n    "format": {\n      "type": "json_schema",\n      "description": null,\n      "name": "schema_response",\n      "schema": {\n        "description": "Model representing the response from the prose-to-schema prompt.",\n        "examples": [\n          {\n            "created_json_schema_definition": {\n              "properties": {\n                "name": {\n                  "type": "string"\n                },\n                "email": {\n                  "format": "email",\n                  "type": "string"\n                },\n                "age": {\n                  "minimum": 0,\n                  "type": "integer"\n                }\n              },\n              "required": [\n                "name",\n                "email"\n              ],\n              "type": "object"\n            },\n            "response_annotation": "A schema for a user profile with name, email, and age fields"\n          }\n        ],\n        "properties": {\n          "response_annotation": {\n            "description": "A brief/concise prose description of what JSON schema was inferred from the user\'s input",\n            "title": "Response Annotation",\n            "type": "string"\n          },\n          "created_json_schema_definition": {\n            "description": "The created JSON schema object returned by the assistant after careful consideration of the user\'s input. Should be a valid JSON schema object; properties object should always be specified.",\n            "properties": {\n              "type": {\n                "type": "string"\n              },\n              "properties": {\n                "type": "object"\n              },\n              "required": {\n                "items": {\n                  "type": "string"\n                },\n                "type": "array"\n              },\n              "additionalProperties": {\n                "type": "boolean"\n              }\n            },\n            "required": [\n              "type",\n              "properties",\n              "required",\n              "additionalProperties"\n            ],\n            "title": "Created Json Schema Definition",\n            "type": "object"\n          }\n        },\n        "required": [\n          "response_annotation",\n          "created_json_schema_definition"\n        ],\n        "title": "SchemaResponse",\n        "type": "object"\n      },\n      "strict": false\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [],\n  "top_p": 1.0,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 516,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 68,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 584\n  },\n  "user": null,\n  "metadata": {}\n}'
    result: StreamHistory = process_completion_response(raw_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TEXT

    text_content = result.content_blocks[0].data.text
    expected_text = '{"description":"Attributes defining a car\'s specifications.","properties":{"weight":{"type":"integer","description":"The weight of the car in pounds"},"cost":{"type":"number","description":"The cost of the car in dollars"},"range":{"type":"integer","description":"The range of the car in miles"}},"type":"object"}'
    assert text_content == expected_text


def test_tool_calls():
    """Tests processing a response with tool calls."""
    history: StreamHistory = StreamHistory()

    raw_data: str = '{\n  "id": "resp_682fbc53353c8191b1922cd10e06444b0e0ea84092f81088",\n  "object": "response",\n  "created_at": 1747958867,\n  "status": "completed",\n  "background": false,\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-mini-2024-07-18",\n  "output": [\n    {\n      "id": "fc_682fbc53f51c819186398a6fa3ee698d0e0ea84092f81088",\n      "type": "function_call",\n      "status": "completed",\n      "arguments": "{\\"location\\":\\"Omaha, NE\\"}",\n      "call_id": "call_pvryy59KU1AxfWrVdL0zlkqq",\n      "name": "get_current_weather"\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "service_tier": "default",\n  "store": true,\n  "temperature": 1.0,\n  "text": {\n    "format": {\n      "type": "text"\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [\n    {\n      "type": "function",\n      "description": "Get the current weather in a given location",\n      "name": "get_current_weather",\n      "parameters": {\n        "type": "object",\n        "properties": {\n          "location": {\n            "type": "string",\n            "description": "The city and state, e.g. Omaha, NE"\n          },\n          "unit": {\n            "type": "string",\n            "enum": [\n              "celsius",\n              "fahrenheit"\n            ]\n          }\n        },\n        "required": [\n          "location"\n        ]\n      },\n      "strict": true\n    },\n    {\n      "type": "function",\n      "description": "Get the forecast for a given location",\n      "name": "get_forecast",\n      "parameters": {\n        "type": "object",\n        "properties": {\n          "location": {\n            "type": "string",\n            "description": "The city and state, e.g. Omaha, NE"\n          },\n          "days": {\n            "type": "integer",\n            "description": "The number of days to forecast",\n            "minimum": 1,\n            "maximum": 7\n          }\n        }\n      },\n      "strict": true\n    }\n  ],\n  "top_p": 1.0,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 140,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 20,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 160\n  },\n  "user": null,\n  "metadata": {}\n}'

    result: StreamHistory = process_completion_response(raw_data, history)

    assert len(result.content_blocks) == 1
    assert result.content_blocks[0].type == ContentBlockType.TOOL_CALL

    tool_data = result.content_blocks[0].data
    assert tool_data.name == "get_current_weather"
    assert tool_data.input == {"location": "Omaha, NE"}

    expected_json_str = '{"location":"Omaha, NE"}'
    assert tool_data.input_json_string == expected_json_str


def test_multiple_content_items():
    """Tests processing a response with multiple content items (text and tool call)."""
    history: StreamHistory = StreamHistory()
    raw_data: str = """{
      "id": "resp_abc123",
      "object": "response",
      "created_at": 1747545603,
      "status": "completed",
      "model": "gpt-4o",
      "output": [
        {
          "id": "msg_xyz789",
          "type": "message",
          "status": "completed",
          "content": [
            {
              "type": "output_text",
              "annotations": [],
              "text": "Let me check the weather for you."
            },
            {
              "type": "tool_use",
              "name": "get_current_weather",
              "input": {
                "location": "Boston, MA",
                "unit": "fahrenheit"
              }
            }
          ],
          "role": "assistant"
        }
      ]
    }"""

    result: StreamHistory = process_completion_response(raw_data, history)

    # Check content blocks - should have both text and tool call
    assert len(result.content_blocks) == 2
    assert result.content_blocks[0].type == ContentBlockType.TEXT
    assert result.content_blocks[0].data.text == "Let me check the weather for you."
    assert result.content_blocks[1].type == ContentBlockType.TOOL_CALL

    # Check tool call data
    tool_data = result.content_blocks[1].data
    assert tool_data.name == "get_current_weather"
    assert tool_data.input == {"location": "Boston, MA", "unit": "fahrenheit"}
