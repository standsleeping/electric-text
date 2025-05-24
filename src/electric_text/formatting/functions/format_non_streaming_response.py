from typing import Any, Optional, Type


def format_non_streaming_response(
    *, content: str, is_valid: bool = False, parsed_model: Optional[Any] = None, model_class: Optional[Type[Any]] = None
) -> str:
    """Format a non-streaming response for output.

    Args:
        content: The formatted content string
        is_valid: Whether the parsed model is valid
        parsed_model: The parsed model instance if available
        model_class: Optional model class for structured outputs

    Returns:
        Formatted string ready for output
    """
    if model_class and is_valid and parsed_model:
        formatted_model = parsed_model.model_dump_json(indent=2)
        return f"RESULT (STRUCTURED): {parsed_model}\n{formatted_model}"
    else:
        # Format using provided content
        if content:
            return f"RESULT (UNSTRUCTURED):\n{content}"
        else:
            return "RESULT (UNSTRUCTURED): [No content available]"
