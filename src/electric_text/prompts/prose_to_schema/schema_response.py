from typing import Dict, Any
from pydantic import BaseModel, Field


class SchemaResponse(BaseModel):
    """Model to capture LLM response containing a string and JSON schema."""

    response_annotation: str = Field(
        description="A brief/concise prose description of what JSON schemayou inferred from the user's input"
    )

    json_schema: Dict[str, Any] = Field(
        description="The JSON schema object returned by the assistant after careful consideration of the user's input"
    )
