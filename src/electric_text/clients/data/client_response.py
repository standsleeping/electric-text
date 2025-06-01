import json
from dataclasses import dataclass
from typing import Any
from pydantic import ValidationError
from electric_text.clients.data.validation_model import ValidationModel

from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.content_block import ContentBlockType, ToolCallData


@dataclass
class ClientResponse[OutputSchema: ValidationModel]:
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

    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return any(
            block.type == ContentBlockType.TOOL_CALL
            for block in self.stream_history.content_blocks
        )

    @property
    def first_tool_call(self) -> tuple[str, dict[str, Any]] | None:
        """Get first tool call name and inputs, if any."""
        for block in self.stream_history.content_blocks:
            if block.type == ContentBlockType.TOOL_CALL:
                tool_data = block.data
                if isinstance(tool_data, ToolCallData):
                    return (tool_data.name, tool_data.input)
        return None

    @property
    def text_content(self) -> str:
        """Get text content from response."""
        return self.stream_history.extract_text_content()

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
