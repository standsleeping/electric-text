import json
from typing import Any, Optional, Type


def format_streaming_final_output(
    *, full_content: str, model_class: Optional[Type[Any]]
) -> str:
    """Format the final output after streaming is complete.

    Args:
        full_content: The complete content from streaming
        model_class: Optional model class for structured outputs

    Returns:
        Formatted string ready for output
    """
    result = f"Full content: {full_content}"

    if model_class:
        try:
            parsed_json = json.loads(full_content)
            result += f"\nJSON: {parsed_json}"
        except json.JSONDecodeError as e:
            result += f"\nError parsing JSON: {e}"
            result += f"\nStructured full content: {full_content}"

    return result
