import json
from typing import Type
from pydantic import ValidationError
from electric_text.clients.data import ParseResult, ResponseModel
from electric_text.clients.functions.parse_partial_response import (
    parse_partial_response,
)


def create_parse_result(
    content: str, response_model: Type[ResponseModel]
) -> ParseResult[ResponseModel]:
    """Parse raw response content into structured model."""
    try:
        parsed_content = parse_partial_response(content)
        try:
            model_instance = response_model(**parsed_content)
            return ParseResult(
                raw_content=content,
                parsed_content=parsed_content,
                model=model_instance,
            )
        except (ValidationError, TypeError) as error:
            return ParseResult(
                raw_content=content,
                parsed_content=parsed_content,
                validation_error=error,
            )
    except json.JSONDecodeError as error:
        return ParseResult(
            raw_content=content,
            parsed_content={},
            json_error=error,
        )

