"""
A provider's test_process_completion_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory

from electric_text.providers.model_providers.openai.functions.process_completion_response import (
    process_completion_response,
)

def test_unstructured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{\n  "id": "resp_68296e0303e88191bb97635af8f14f150bb08925da38f793",\n  "object": "response",\n  "created_at": 1747545603,\n  "status": "completed",\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-mini-2024-07-18",\n  "output": [\n    {\n      "id": "msg_68296e03592c8191b24da99b0fdada0a0bb08925da38f793",\n      "type": "message",\n      "status": "completed",\n      "content": [\n        {\n          "type": "output_text",\n          "annotations": [],\n          "text": "dusty asphalt wakes\\u2014  \\ngreen shoots sip the heavy air,  \\nearth\'s breath, warm and sweet."\n        }\n      ],\n      "role": "assistant"\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "service_tier": "default",\n  "store": true,\n  "temperature": 1.0,\n  "text": {\n    "format": {\n      "type": "text"\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [],\n  "top_p": 1.0,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 112,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 23,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 135\n  },\n  "user": null,\n  "metadata": {}\n}'
    result: StreamHistory = process_completion_response(raw_data, history)
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[0].content == "dusty asphalt wakes—  \ngreen shoots sip the heavy air,  \nearth's breath, warm and sweet."

def test_structured_content():
    history: StreamHistory = StreamHistory()
    raw_data: str = '{\n  "id": "resp_68296f8d9de481918035c4cd6fd7c86b0226c27a0a5b5572",\n  "object": "response",\n  "created_at": 1747545997,\n  "status": "completed",\n  "error": null,\n  "incomplete_details": null,\n  "instructions": null,\n  "max_output_tokens": null,\n  "model": "gpt-4o-mini-2024-07-18",\n  "output": [\n    {\n      "id": "msg_68296f8df07c8191993b14962d4db7df0226c27a0a5b5572",\n      "type": "message",\n      "status": "completed",\n      "content": [\n        {\n          "type": "output_text",\n          "annotations": [],\n          "text": "{\\"description\\":\\"Attributes defining a car\'s specifications.\\",\\"properties\\":{\\"weight\\":{\\"type\\":\\"integer\\",\\"description\\":\\"The weight of the car in pounds\\"},\\"cost\\":{\\"type\\":\\"number\\",\\"description\\":\\"The cost of the car in dollars\\"},\\"range\\":{\\"type\\":\\"integer\\",\\"description\\":\\"The range of the car in miles\\"}},\\"type\\":\\"object\\"}"\n        }\n      ],\n      "role": "assistant"\n    }\n  ],\n  "parallel_tool_calls": true,\n  "previous_response_id": null,\n  "reasoning": {\n    "effort": null,\n    "summary": null\n  },\n  "service_tier": "default",\n  "store": true,\n  "temperature": 1.0,\n  "text": {\n    "format": {\n      "type": "json_schema",\n      "description": null,\n      "name": "schema_response",\n      "schema": {\n        "description": "Model representing the response from the prose-to-schema prompt.",\n        "examples": [\n          {\n            "created_json_schema_definition": {\n              "properties": {\n                "name": {\n                  "type": "string"\n                },\n                "email": {\n                  "format": "email",\n                  "type": "string"\n                },\n                "age": {\n                  "minimum": 0,\n                  "type": "integer"\n                }\n              },\n              "required": [\n                "name",\n                "email"\n              ],\n              "type": "object"\n            },\n            "response_annotation": "A schema for a user profile with name, email, and age fields"\n          }\n        ],\n        "properties": {\n          "response_annotation": {\n            "description": "A brief/concise prose description of what JSON schema was inferred from the user\'s input",\n            "title": "Response Annotation",\n            "type": "string"\n          },\n          "created_json_schema_definition": {\n            "description": "The created JSON schema object returned by the assistant after careful consideration of the user\'s input. Should be a valid JSON schema object; properties object should always be specified.",\n            "properties": {\n              "type": {\n                "type": "string"\n              },\n              "properties": {\n                "type": "object"\n              },\n              "required": {\n                "items": {\n                  "type": "string"\n                },\n                "type": "array"\n              },\n              "additionalProperties": {\n                "type": "boolean"\n              }\n            },\n            "required": [\n              "type",\n              "properties",\n              "required",\n              "additionalProperties"\n            ],\n            "title": "Created Json Schema Definition",\n            "type": "object"\n          }\n        },\n        "required": [\n          "response_annotation",\n          "created_json_schema_definition"\n        ],\n        "title": "SchemaResponse",\n        "type": "object"\n      },\n      "strict": false\n    }\n  },\n  "tool_choice": "auto",\n  "tools": [],\n  "top_p": 1.0,\n  "truncation": "disabled",\n  "usage": {\n    "input_tokens": 516,\n    "input_tokens_details": {\n      "cached_tokens": 0\n    },\n    "output_tokens": 68,\n    "output_tokens_details": {\n      "reasoning_tokens": 0\n    },\n    "total_tokens": 584\n  },\n  "user": null,\n  "metadata": {}\n}'
    result: StreamHistory = process_completion_response(raw_data, history)
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK

def test_tool_calls():
    # TODO: Implement this test
    pass