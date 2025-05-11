import json
from dataclasses import dataclass
from pydantic import ValidationError
from typing import (
    Any,
    Optional,
    TypeVar,
    Union,
)

from electric_text.clients.data.validation_model import ValidationModel


# Use ValidationModel instead of defining JSONResponse
ResponseType = TypeVar("ResponseType", bound="ValidationModel", contravariant=True)

ResponseModel = TypeVar("ResponseModel", bound=ValidationModel)


@dataclass
class ParseResult[ResponseModel]:
    """Wrapper for parsed response data that may be incomplete."""

    raw_content: str
    parsed_content: dict[str, Any]
    model: Optional[ResponseModel] = None
    validation_error: Optional[Union[ValidationError, TypeError]] = None
    json_error: Optional[json.JSONDecodeError] = None

    @property
    def is_valid(self) -> bool:
        """Checks for a valid model."""
        return self.model is not None
