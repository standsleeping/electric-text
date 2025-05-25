import json
from dataclasses import dataclass
from typing import Any
from pydantic import ValidationError, BaseModel

from electric_text.providers.data.stream_history import StreamHistory


@dataclass
class ClientResponse[OutputSchema: BaseModel]:
    """
    Represents a unified response from a provider.
    Contains either a raw prompt result or a parsed structured result.
    """

    stream_history: StreamHistory
    parsed_content: dict[str, Any] | None = None
    validated_output: OutputSchema | None = None
    validation_error: ValidationError | TypeError | None = None
    json_error: json.JSONDecodeError | None = None

    @property
    def is_valid(self) -> bool:
        """Checks for a valid model."""
        return self.validated_output is not None

    def __str__(self) -> str:
        """
        String representation of the ClientResponse.
        If errors are present, return them. Otherwise, return the stream history.
        """
        if self.validation_error is not None:
            return "Validation Error!"
        elif self.json_error is not None:
            return "JSON Error!"
        else:
            return str(self.stream_history)
