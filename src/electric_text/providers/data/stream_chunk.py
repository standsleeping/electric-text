from typing import Optional
from dataclasses import dataclass

from electric_text.providers.data.stream_chunk_type import StreamChunkType


@dataclass
class StreamChunk:
    type: StreamChunkType
    raw_line: str
    parsed_data: Optional[dict[str, str]] = None
    content: Optional[str] = None
    error: Optional[str] = None
