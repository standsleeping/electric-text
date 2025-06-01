from typing import Type
from electric_text.clients.data.validation_model import ValidationModel
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.clients.data import ClientResponse
from electric_text.clients.functions.create_parse_result import create_parse_result


async def history_to_client_response[OutputSchema: ValidationModel](
    history: StreamHistory, output_schema: Type[OutputSchema]
) -> ClientResponse[OutputSchema]:
    """Convert a StreamHistory to a ClientResponse.

    Args:
        history: The StreamHistory to convert

    Returns:
        The ClientResponse
    """
    text_content = history.extract_text_content()

    parsed_content, validated_instance, validation_error, json_error = (
        create_parse_result(text_content, output_schema)
    )

    return ClientResponse[OutputSchema](
        stream_history=history,
        parsed_content=parsed_content,  # Could be {} or { key: value, ... }
        validated_output=validated_instance,  # Could be None or an instance of the output schema
        validation_error=validation_error,  # Could be ValidationError or TypeError or None
        json_error=json_error,  # Could be JSONDecodeError or None
    )
