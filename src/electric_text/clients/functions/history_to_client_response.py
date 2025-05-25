from typing import Type, cast
from pydantic import BaseModel
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.clients.data import ClientResponse
from electric_text.clients.functions.create_parse_result import create_parse_result


async def history_to_client_response[OutputSchema: BaseModel](
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
        parsed_content=parsed_content,
        validated_output=cast(OutputSchema | None, validated_instance),
        validation_error=validation_error,
        json_error=json_error,
    )
