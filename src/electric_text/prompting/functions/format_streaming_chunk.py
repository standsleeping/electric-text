from typing import Any, Optional, Type

from electric_text.clients.data.client_response import ClientResponse


def format_streaming_chunk(
    *, chunk: ClientResponse[Any], model_class: Optional[Type[Any]]
) -> str:
    """Format a streaming chunk for output.

    Args:
        chunk: The ClientResponse chunk to format
        model_class: Optional model class for structured outputs

    Returns:
        Formatted string ready for output
    """
    if model_class and chunk.is_valid and chunk.parsed_model:
        formatted_model = chunk.parsed_model.model_dump_json(indent=2)
        return f"Valid chunk: {chunk.parsed_model}\n{formatted_model}"
    else:
        return f"Raw chunk content: {chunk.raw_content}"
