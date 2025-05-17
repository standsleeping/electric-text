from datetime import datetime
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.functions.process_content import (
    process_content,
)
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)
from electric_text.providers.model_providers.ollama.data.message import Message


def test_process_content_creates_content_chunk():
    """Creates a content chunk from a model response."""
    message = Message(role="assistant", content="Hello, world!")
    raw_line = '{"message": {"content": "Hello, world!"}}'

    response = ModelResponse(
        model="llama3.1:8b",
        created_at=datetime.now(),
        message=message,
        done_reason="",
        done=False,
        total_duration=100,
        load_duration=10,
        prompt_eval_count=5,
        prompt_eval_duration=20,
        eval_count=10,
        eval_duration=30,
        raw_line=raw_line,
    )

    chunk = process_content(response)

    assert chunk.type == StreamChunkType.CONTENT_CHUNK
    assert chunk.content == "Hello, world!"
    assert chunk.raw_line == raw_line
