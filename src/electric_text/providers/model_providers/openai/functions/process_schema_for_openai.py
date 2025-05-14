from typing import Any, Dict

from electric_text.providers.model_providers.openai.data.format_error import FormatError
from electric_text.providers.model_providers.openai.functions.process_nested_schemas import (
    process_nested_schemas,
)


def process_schema_for_openai(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a JSON schema to ensure it meets OpenAI's requirements.

    Args:
        schema: The JSON schema to process

    Returns:
        The processed schema

    Raises:
        FormatError: If the schema doesn't meet OpenAI's requirements
    """
    # Check root schema is an object type
    if schema.get("type") != "object":
        raise FormatError(
            "Root schema must be of type 'object' for OpenAI structured outputs"
        )

    # Check if 'additionalProperties' is set to false for object properties
    if "additionalProperties" not in schema:
        schema["additionalProperties"] = False

    # Ensure all properties are required
    if "properties" in schema and "required" not in schema:
        schema["required"] = list(schema["properties"].keys())

    # Remove unsupported keywords
    unsupported_keywords = ["examples", "$comment", "default"]
    for keyword in unsupported_keywords:
        if keyword in schema:
            del schema[keyword]

    # Process nested schemas
    process_nested_schemas(schema, unsupported_keywords)

    return schema
