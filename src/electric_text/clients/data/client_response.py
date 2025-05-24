from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Any, Union, cast
import json
from pydantic import ValidationError

from electric_text.clients.data import PromptResult, ParseResult

ResponseModel = TypeVar("ResponseModel")


@dataclass
class ClientResponse(Generic[ResponseModel]):
    """
    Represents a unified response from a provider.
    Contains either a raw prompt result or a parsed structured result.
    """

    # Store the original result
    raw_result: Union[PromptResult, ParseResult[ResponseModel]]


    @property
    def is_parsed(self) -> bool:
        """Check if this response contains a parsed result."""
        return isinstance(self.raw_result, ParseResult)

    @property
    def parsed_model(self) -> Optional[ResponseModel]:
        """Get the parsed model if available, otherwise None."""
        if self.is_parsed:
            return self.raw_result.model  # type: ignore[union-attr]
        return None

    @property
    def is_valid(self) -> bool:
        """Check if the parsed result is valid (if parsed)."""
        if self.is_parsed:
            return self.raw_result.is_valid  # type: ignore[union-attr]
        return False

    @property
    def validation_error(
        self,
    ) -> Optional[Union[ValidationError, TypeError, json.JSONDecodeError]]:
        """Get any validation error if available."""
        if self.is_parsed:
            result = cast(ParseResult[ResponseModel], self.raw_result)
            if result.validation_error:
                return result.validation_error
            return result.json_error
        return None

    @classmethod
    def from_prompt_result(cls, result: PromptResult) -> "ClientResponse[Any]":
        """Create a ClientResponse from a PromptResult."""
        return cls(raw_result=result)

    def get_formatted_content(self) -> str:
        """Get formatted content from the response for display purposes."""
        if hasattr(self.raw_result, 'content_blocks') and self.raw_result.content_blocks:
            from electric_text.providers.functions.format_content_blocks import format_content_blocks
            return format_content_blocks(content_blocks=self.raw_result.content_blocks)
        return ""

    @classmethod
    def from_parse_result(
        cls, result: ParseResult[ResponseModel]
    ) -> "ClientResponse[ResponseModel]":
        """Create a ClientResponse from a ParseResult."""
        return cls(raw_result=result)
