"""
A provider's test_process_stream_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.content_block import ContentBlock, ContentBlockType
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
        "event: content_block_stop",
        'data: {"type":"content_block_stop","index":0      }',
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

    content_block: ContentBlock = history.content_blocks[0]

    assert content_block.type == ContentBlockType.TEXT

    expected_text: str = (
        "Petrichor rises  \n"
        + "Corn unfurls to catch droplets  \n"
        + "Earth speaks to lightning"
    )

    actual_text: str = content_block.data.text

    assert actual_text == expected_text


def test_structured_content():
    history: StreamHistory = StreamHistory()

    chunks: list[str] = [
        "event: message_start",
        'data: {"type":"message_start","message":{"id":"msg_01CFsS5HEkAPzg4t3TRAkQoN","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":447,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":5}}               }',
        "",
        "event: content_block_start",
        'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}               }',
        "",
        "event: ping",
        'data: {"type": "ping"}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\n  \\"type\\":"}              }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" \\"object\\",\\n  "}     }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\"description\\": \\"Attributes of"}    }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" a vehicle\\",\\n  \\"properties"}        }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\": {\\n    \\"weight\\": {\\n      "}      }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\"type\\": \\"number"}               }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\",\\n      \\"description"}          }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\": \\"The weight of the vehicle in"}              }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" pounds\\"\\n    },\\n    "}               }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\"price\\": {\\n      \\""}            }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"type\\": \\"number\\","}       }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\n      \\"description\\":"}    }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" \\"The cost of the vehicle in"}  }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" dollars\\"\\n    },\\n    \\"range\\":"}      }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" {\\n      \\"type"}       }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\": \\"number\\","}   }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\n      \\"description\\": \\""} }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"The maximum distance the vehicle can travel in"}             }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" miles\\"\\n    }\\n  },"} }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\n  \\"required\\":"}            }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" [\\"weight\\", \\"price"}         }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\", \\"range\\"]"}     }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\\n}"}   }',
        "",
        "event: content_block_stop",
        'data: {"type":"content_block_stop","index":0      }',
        "",
        "event: message_delta",
        'data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":143}     }',
        "",
        "event: message_stop",
        'data: {"type":"message_stop"}',
        "",
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    content_block: ContentBlock = history.content_blocks[0]

    assert content_block.type == ContentBlockType.TEXT

    expected_text: str = '\n  "type": "object",\n  "description": "Attributes of a vehicle",\n  "properties": {\n    "weight": {\n      "type": "number",\n      "description": "The weight of the vehicle in pounds"\n    },\n    "price": {\n      "type": "number",\n      "description": "The cost of the vehicle in dollars"\n    },\n    "range": {\n      "type": "number",\n      "description": "The maximum distance the vehicle can travel in miles"\n    }\n  },\n  "required": ["weight", "price", "range"]\n}'

    actual_text: str = content_block.data.text

    assert actual_text == expected_text


def test_tool_calls():
    history: StreamHistory = StreamHistory()

    chunks: list[str] = [
        "event: message_start",
        'data: {"type":"message_start","message":{"id":"msg_01VGAt4hT8PneoBcTp25DJRH","type":"message","role":"assistant","model":"claude-3-7-sonnet-20250219","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":544,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":1}}         }',
        "",
        "event: content_block_start",
        'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}       }',
        "",
        "event: ping",
        'data: {"type": "ping"}',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"I"}               }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\'d be happy to check the current weather in"}         }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" Omaha for you. Let me get that"}     }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" information right away."}}',
        "",
        "event: content_block_stop",
        'data: {"type":"content_block_stop","index":0        }',
        "",
        "event: content_block_start",
        'data: {"type":"content_block_start","index":1,"content_block":{"type":"tool_use","id":"toolu_01YK5wzBVm7A11WtLyDn2p9i","name":"get_current_weather","input":{}}           }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":""}         }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"{\\"locati"} }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"on\\": \\""}           }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"Omaha, N"}               }',
        "",
        "event: content_block_delta",
        'data: {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":"E\\"}"}             }',
        "",
        "event: content_block_stop",
        'data: {"type":"content_block_stop","index":1  }',
        "",
        "event: message_delta",
        'data: {"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":null},"usage":{"output_tokens":85}              }',
        "",
        "event: message_stop",
        'data: {"type":"message_stop"     }',
        "",
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    first_block: ContentBlock = history.content_blocks[0]

    assert first_block.type == ContentBlockType.TEXT

    expected_text: str = "I'd be happy to check the current weather in Omaha for you. Let me get that information right away."

    actual_text: str = first_block.data.text

    assert actual_text == expected_text

    second_block: ContentBlock = history.content_blocks[1]

    assert second_block.type == ContentBlockType.TOOL_CALL

    assert second_block.data.name == "get_current_weather"

    expected_input_json_string: str = '{"location": "Omaha, NE"}'

    actual_input_json_string: str = second_block.data.input_json_string

    assert actual_input_json_string == expected_input_json_string
