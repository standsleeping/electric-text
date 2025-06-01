from typing import Protocol, Any, Dict, Type
from typing_extensions import runtime_checkable


@runtime_checkable
class ValidationModel(Protocol):
    """Protocol for validation models.

    This protocol defines the interface for validation models, allowing the
    clients package to handle the specifics of validation implementation
    while providing a simple interface for dependent packages.

    This separation gives us flexibility to evolve validation approaches
    without affecting higher-level code, and keeps validation concerns
    properly encapsulated at the data layer.
    """

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        """Return JSON schema for the model."""
        ...

    def model_dump(self) -> Dict[str, Any]:
        """Return model data as a dictionary."""
        ...


# Type alias for validation model classes
ValidationModelType = Type[ValidationModel]
