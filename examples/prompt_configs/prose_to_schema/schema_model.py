from pydantic import BaseModel, Field
from typing import Dict, Any


class SchemaResponse(BaseModel):
    """Model representing the response from the prose-to-schema prompt."""

    response_annotation: str = Field(
        description="A brief/concise prose description of what JSON schema was inferred from the user's input"
    )

    created_json_schema_definition: Dict[str, Any] = Field(
        description="The created JSON schema object returned by the assistant after careful consideration of the user's input. Should be a valid JSON schema object; properties object should always be specified.",
        json_schema_extra={
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "properties": {"type": "object"},
                "required": {"type": "array", "items": {"type": "string"}},
                "additionalProperties": {"type": "boolean"},
            },
            "required": ["type", "properties", "required", "additionalProperties"]
        },
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response_annotation": "A schema for a user profile with name, email, and age fields",
                    "created_json_schema_definition": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "age": {"type": "integer", "minimum": 0},
                        },
                        "required": ["name", "email"],
                    },
                }
            ]
        }
    }
