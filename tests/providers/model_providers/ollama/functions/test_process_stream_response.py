"""
A provider's test_process_stream_response.py file contains the following standard tests:

- Unstructured content (a poem)
- Structured content (a schema)
- Tool calls

"""

from electric_text.providers.data.content_block import ContentBlock, ContentBlockType
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.model_providers.ollama.functions.process_stream_response import (
    process_stream_response,
)


def test_unstructured_content():
    history: StreamHistory = StreamHistory()

    chunks: list[str] = [
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"LINE1\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:01.111111Z","message":{"role":"assistant","content":"LINE2\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:02.222222Z","message":{"role":"assistant","content":"LINE3\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:03.333333Z","message":{"role":"assistant","content":""},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}',
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    content_block: ContentBlock = history.content_blocks[0]

    assert content_block.type == ContentBlockType.TEXT

    expected_text: str = "LINE1\nLINE2\nLINE3\n"

    actual_text: str = content_block.data.text

    assert actual_text == expected_text


def test_structured_content():
    history: StreamHistory = StreamHistory()

    chunks: list[str] = [
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"{\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"re"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"sp"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"ons"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"e"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"_"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"annot"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"at"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"ion"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"Car"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" attributes"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\",\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"create"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"d"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"_"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"json"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"_schema"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"_"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"definition"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" {\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"   "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"type"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"object"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\",\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"   "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"properties"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" {\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"weight"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" {\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"type"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"integer"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\",\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"description"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"The"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" weight"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" of"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" the"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" car"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" in"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" pounds"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\"\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" },\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"price"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" {\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"type"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"number"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\",\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"description"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"The"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" price"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" of"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" the"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" car"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\"\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" },\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"range"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" {\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"type"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"number"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\",\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"       "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"description"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"The"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" driving"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" range"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" of"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" the"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" car"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" in"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" miles"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\"\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"     "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" }\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"   "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" },\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"   "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"required"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" [\\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"weight"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\","},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"price"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\","},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"range"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\"],\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"   "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" \\""},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"additional"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"Properties"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\":"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" false"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" "},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":" }\\n"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"}"},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":""},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}',
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    assert len(history.chunks) == 145
    assert history.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
    assert history.chunks[-1].type == StreamChunkType.COMPLETION_END


def test_tool_calls():
    history: StreamHistory = StreamHistory()

    chunks: list[str] = [
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":"","tool_calls":[{"function":{"name":"get_weather","arguments":{"city":"Omaha"}}}]},"done":false}',
        '{"model":"llama3.1:8b","created_at":"2025-01-10T12:12:00.000000Z","message":{"role":"assistant","content":""},"done_reason":"stop","done":true,"total_duration":99,"load_duration":99,"prompt_eval_count":99,"prompt_eval_duration":99,"eval_count":99,"eval_duration":99}',
    ]

    for chunk in chunks:
        history: StreamHistory = process_stream_response(chunk, history)

    assert len(history.chunks) == 2
    assert history.chunks[0].type == StreamChunkType.FULL_TOOL_CALL
    assert history.chunks[1].type == StreamChunkType.COMPLETION_END
