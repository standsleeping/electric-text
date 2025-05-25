from dataclasses import dataclass
from typing import Optional, Type, Any

from electric_text.clients.data.model_load_result import ModelLoadResult
from electric_text.prompting.data.model_load_error import ModelLoadError
from electric_text.clients.data.default_output_schema import DefaultOutputSchema
from pydantic import BaseModel


@dataclass
class ModelResult:
    """Result of loading a validation model from a Python file."""

    loaded_model_class: Optional[Type[BaseModel]] = None
    error: Optional[ModelLoadError] = None
    error_message: Optional[str] = None

    @property
    def model_class(self) -> Type[BaseModel]:
        """Returns the loaded model class if it exists."""
        if self.loaded_model_class is None:
            return DefaultOutputSchema
        return self.loaded_model_class

    @property
    def is_valid(self) -> bool:
        """Returns True if a valid model was loaded."""
        return self.loaded_model_class is not None and self.error is None

    @classmethod
    def from_load_result(cls, result: ModelLoadResult) -> "ModelResult":
        """Convert a ModelLoadResult to a ModelResult."""
        error = None
        if result.error:
            if result.error == "NOT_FOUND":
                error = ModelLoadError.NOT_FOUND
            elif result.error == "IMPORT_ERROR":
                error = ModelLoadError.IMPORT_ERROR
            elif result.error == "NO_MODEL":
                error = ModelLoadError.NO_MODEL
            else:
                error = ModelLoadError.OTHER

        return cls(
            loaded_model_class=result.model_class,
            error=error,
            error_message=result.error_message,
        )
