from typing import Any, Optional, Type

from electric_text.clients.data.client_response import ClientResponse


def format_non_streaming_response(
    *, response: ClientResponse[Any], model_class: Optional[Type[Any]]
) -> str:
    """Format a non-streaming client response for output.

    Args:
        response: The ClientResponse to format
        model_class: Optional model class for structured outputs

    Returns:
        Formatted string ready for output
    """
    if model_class and response.is_valid and response.parsed_model:
        formatted_model = response.parsed_model.model_dump_json(indent=2)
        return f"RESULT (STRUCTURED): {response.parsed_model}\n{formatted_model}"
    else:
        return f"RESULT (UNSTRUCTURED): {response.raw_content}"
