import json
from typing import Type, Dict, Any, Optional, Union, Tuple
from pydantic import ValidationError
from electric_text.clients.data.validation_model import ValidationModel
from electric_text.clients.functions.parse_partial_response import (
    parse_partial_response,
)


def create_parse_result[OutputSchema: ValidationModel](
    content: str, output_schema: Type[OutputSchema]
) -> Tuple[
    Dict[str, Any],
    Optional[OutputSchema],
    Optional[Union[ValidationError, TypeError]],
    Optional[json.JSONDecodeError],
]:
    """Parse raw response content into a validated instance of the output schema.

    Returns:
        Tuple of (parsed_content, validated_instance, validation_error, json_error)
    """
    try:
        parsed_content = parse_partial_response(content)
        try:
            model_instance = output_schema(**parsed_content)
            return (parsed_content, model_instance, None, None)
        except (ValidationError, TypeError) as error:
            return (parsed_content, None, error, None)
    except json.JSONDecodeError as error:
        return ({}, None, None, error)
