from enum import Enum


class StreamChunkType(Enum):
    INITIAL_MESSAGE = "initial_message"  # First chunk with role/content
    CONTENT_CHUNK = "content_chunk"  # Regular content chunk
    COMPLETION_END = "completion_end"  # Empty delta with finish_reason "stop"
    STREAM_DONE = "stream_done"  # [DONE] marker
    EMPTY_LINE = "empty_line"  # Empty line
    INVALID_FORMAT = "invalid_format"  # Does not start with "data: "
    NO_CHOICES = "no_choices"  # Missing choices array
    PARSE_ERROR = "parse_error"  # JSON parse error
    COMPLETE_RESPONSE = "COMPLETE_RESPONSE"  # Non-streaming response
    HTTP_ERROR = "HTTP_ERROR"  # HTTP error
    FORMAT_ERROR = "FORMAT_ERROR"  # Response format doesn't match expected schema
    PREFILLED_CONTENT = "prefilled_content"  # Content that was prefilled in the prompt
    UNHANDLED_LINE = "unhandled_line"  # Line that we haven't handled yet
