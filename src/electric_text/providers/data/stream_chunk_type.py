from enum import Enum
from dataclasses import dataclass


@dataclass
class StreamChunkType(Enum):
    FULL_TOOL_CALL = "full_tool_call"
    
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

    # Response lifecycle events
    RESPONSE_CREATED = "response.created"
    RESPONSE_IN_PROGRESS = "response.in_progress"
    RESPONSE_COMPLETED = "response.completed"
    RESPONSE_FAILED = "response.failed"
    RESPONSE_INCOMPLETE = "response.incomplete"

    # Output item events
    OUTPUT_ITEM_ADDED = "response.output_item.added"
    OUTPUT_ITEM_DONE = "response.output_item.done"

    # Content part events
    CONTENT_PART_ADDED = "response.content_part.added"
    CONTENT_PART_DONE = "response.content_part.done"

    # Output text events
    OUTPUT_TEXT_DELTA = "response.output_text.delta"
    OUTPUT_TEXT_DONE = "response.output_text.done"

    # Text annotation events
    TEXT_ANNOTATION_ADDED = "response.output_text.annotation.added"

    # Refusal events
    REFUSAL_DELTA = "response.refusal.delta"
    REFUSAL_DONE = "response.refusal.done"

    # Function call events
    FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"

    # File search events
    FILE_SEARCH_CALL_IN_PROGRESS = "response.file_search_call.in_progress"
    FILE_SEARCH_CALL_SEARCHING = "response.file_search_call.searching"
    FILE_SEARCH_CALL_COMPLETED = "response.file_search_call.completed"

    # Web search events
    WEB_SEARCH_CALL_IN_PROGRESS = "response.web_search_call.in_progress"
    WEB_SEARCH_CALL_SEARCHING = "response.web_search_call.searching"
    WEB_SEARCH_CALL_COMPLETED = "response.web_search_call.completed"

    # Reasoning summary events
    REASONING_SUMMARY_PART_ADDED = "response.reasoning_summary_part.added"
    REASONING_SUMMARY_PART_DONE = "response.reasoning_summary_part.done"
    REASONING_SUMMARY_TEXT_DELTA = "response.reasoning_summary_text.delta"
    REASONING_SUMMARY_TEXT_DONE = "response.reasoning_summary_text.done"
