from typing import Any, Dict, Optional, Protocol, Type, TypeVar, runtime_checkable


@runtime_checkable
class ValidationModel(Protocol):
    """Protocol defining the required structure for validation model objects."""

    def __init__(self, **kwargs: Any) -> None: ...

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]: ...


# Type variable for validation model type, bounded by ValidationModel
ValidationModelType = TypeVar(
    "ValidationModelType",
    bound="ValidationModel",
    contravariant=True,
)


class ModelLoadResult:
    """Result of loading a validation model from a Python file."""

    model_class: Optional[Type[ValidationModel]] = None
    error: Optional[str] = None
    error_message: Optional[str] = None

    def __init__(
        self,
        model_class: Optional[Type[ValidationModel]] = None,
        error: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        self.model_class = model_class
        self.error = error
        self.error_message = error_message

    @property
    def is_valid(self) -> bool:
        """Returns True if a valid model was loaded."""
        return self.model_class is not None and self.error is None
