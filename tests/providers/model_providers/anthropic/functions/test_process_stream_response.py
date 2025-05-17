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

    assert len(history.chunks) == 10


def test_tool_calls():
    # TODO: Implement this test
    pass
