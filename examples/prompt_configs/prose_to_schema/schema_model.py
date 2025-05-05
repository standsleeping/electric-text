from pydantic import BaseModel, Field
from typing import Dict, Any


class SchemaResponse(BaseModel):
    """Model representing the response from the prose-to-schema prompt."""
    
    response_annotation: str = Field(
        description="A brief/concise prose description of what JSON schema was inferred from the user's input"
    )
    
    json_schema: Dict[str, Any] = Field(
        description="The JSON schema object returned by the assistant after careful consideration of the user's input"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response_annotation": "A schema for a user profile with name, email, and age fields",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "age": {"type": "integer", "minimum": 0}
                        },
                        "required": ["name", "email"]
                    }
                }
            ]
        }
    }