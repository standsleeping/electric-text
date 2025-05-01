import json
from dataclasses import dataclass
from pydantic import ValidationError
from typing import (
    Any,
    Dict,
    Optional,
    TypeVar,
    Protocol,
    Union,
    runtime_checkable,
)


@runtime_checkable
class JSONResponse(Protocol):
    """Protocol defining the required structure for response objects."""

    def __init__(self, **kwargs: Any) -> None: ...

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]: ...


# Type variable for response type, bounded by JSONResponse
ResponseType = TypeVar("ResponseType", bound="JSONResponse", contravariant=True)

ResponseModel = TypeVar("ResponseModel", bound=JSONResponse)


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
