from electric_text.providers.data.stream_chunk import StreamChunk
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)


def process_content(response: ModelResponse) -> StreamChunk:
    """
    Processes content from a ModelResponse into a StreamChunk.

    Args:
        response: ModelResponse containing content to process

    Returns:
        StreamChunk containing the processed content
    """
    return StreamChunk(
        type=StreamChunkType.CONTENT_CHUNK,
        raw_line=response.raw_line,
        content=response.message.content,
    )
