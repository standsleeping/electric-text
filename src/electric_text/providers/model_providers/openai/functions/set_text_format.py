import copy
from typing import Any, Dict

from electric_text.providers.model_providers.openai.functions.camel_to_snake import (
    camel_to_snake,
)
from electric_text.providers.model_providers.openai.functions.process_schema_for_openai import (
    process_schema_for_openai,
)


def set_text_format(
    format_schema: Dict[str, Any], strict: bool = True
) -> Dict[str, Any]:
    """
    Configure structured outputs for OpenAI API using JSON schema.

    This function prepares the 'text.format' parameter for the OpenAI API to ensure
    responses adhere to a specific JSON schema structure. It handles:

    1. Setting the format type to "json_schema"
    2. Naming the schema (using snake_case conversion of the schema title)
    3. Applying the schema definition
    4. Setting strictness mode (enforces schema validation)

    Note: OpenAI has specific requirements for JSON schemas:
    - All properties should be marked as required
    - Objects should have additionalProperties set to false
    - Root schema must be an object (not anyOf)
    - Limited nesting (maximum 5 levels)
    - Limited total properties (maximum 100)
    - Certain keywords are not supported (examples, $comment, etc.)

    Args:
        format_schema: The JSON schema definition
        strict: Whether to enforce strict schema validation (default: True)

    Returns:
        Dict containing properly formatted text.format configuration

    Raises:
        FormatError: If the schema doesn't meet OpenAI's requirements when strict=True
    """
    # Create a deep copy to avoid modifying the original schema
    schema = copy.deepcopy(format_schema)

    # Verify schema has a title
    if "title" not in schema:
        # Use a default name if title is missing
        schema_name = "response_schema"
    else:
        schema_name = camel_to_snake(schema["title"])

    # Process the schema if strict mode is enabled
    if strict:
        schema = process_schema_for_openai(schema)

    return {
        "format": {
            "type": "json_schema",
            "name": schema_name,
            "schema": schema,
            "strict": strict,
        }
    }
