from enum import Enum
from dataclasses import dataclass


@dataclass
class StreamChunkType(Enum):
    # NEW
    STREAM_START = "stream_start"
    FULL_TOOL_CALL = "full_tool_call"
    FULL_TEXT = "full_text"
    TEXT_START = "text_start"
    TEXT_DELTA = "text_delta"
    TEXT_STOP = "text_stop"
    TOOL_START = "tool_start"
    TOOL_DELTA = "tool_delta"
    TOOL_STOP = "tool_stop"
    STREAM_STOP = "stream_stop"
    UNHANDLED_EVENT = "unhandled_event"
    PARSE_ERROR = "parse_error"

    # OLD
    INITIAL_MESSAGE = "initial_message"
    INFO_MARKER = "info_marker"
    CONTENT_CHUNK = "content_chunk"
    PREFILLED_CONTENT = "prefilled_content"
    COMPLETION_END = "completion_end"
    UNHANDLED_LINE = "unhandled_line"
    HTTP_ERROR = "http_error"
    UNRECOGNIZED_EVENT = "unrecognized_event"

