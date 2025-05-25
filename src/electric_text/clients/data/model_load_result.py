from dataclasses import dataclass
from typing import Optional, Type
from pydantic import BaseModel


@dataclass
class ModelLoadResult:
    """Result of loading a validation model from a Python file."""

    model_class: Optional[Type[BaseModel]] = None
    error: Optional[str] = None
    error_message: Optional[str] = None

    def __init__(
        self,
        model_class: Optional[Type[BaseModel]] = None,
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
