from enum import Enum
from dataclasses import dataclass


@dataclass
class StreamChunkType(Enum):
    # NEW
    TOOL_CALL = "tool_call"

    # OLD
    INITIAL_MESSAGE = "initial_message"
    INFO_MARKER = "info_marker"
    FULL_TOOL_CALL = "full_tool_call"
    CONTENT_CHUNK = "content_chunk"
    PREFILLED_CONTENT = "prefilled_content"
    COMPLETION_END = "completion_end"
    UNHANDLED_LINE = "unhandled_line"
    PARSE_ERROR = "parse_error"
    HTTP_ERROR = "http_error"
    UNRECOGNIZED_EVENT = "unrecognized_event"

