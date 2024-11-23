from typing import Dict, Any
from pydantic import BaseModel, Field


class SchemaResponse(BaseModel):
    """Model to capture LLM response containing a string and JSON schema."""

    response_text: str = Field(
        description="A brief description of the newly-created JSON schema and what it represents"
    )

    json_schema: Dict[str, Any] = Field(
        description="The JSON schema object returned by the assistant after careful consideration of the user's input"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response_text": "The following is a JSON schema for a person.",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string",
                            "description": "The first name of the person",
                        },
                        "last_name": {
                            "type": "string",
                            "description": "The last name of the person",
                        },
                        "nickname": {
                            "type": "string",
                            "description": "An alternate name for the person",
                        },
                        "age": {
                            "type": "integer",
                            "description": "The age of the person",
                        },
                        "hobbies": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "description": "A hobby or general interest of the person",
                            },
                        },
                    },
                },
            }
        }
