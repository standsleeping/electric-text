from typing import Any, Dict, TypeVar, runtime_checkable, Protocol


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
