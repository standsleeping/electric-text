from dataclasses import dataclass
from typing import Optional, Type, Any

from electric_text.clients.data.validation_model import ModelLoadResult
from electric_text.prompting.data.model_load_error import ModelLoadError


@dataclass
class ModelResult:
    """Result of loading a validation model from a Python file."""

    model_class: Optional[Type[Any]] = None
    error: Optional[ModelLoadError] = None
    error_message: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Returns True if a valid model was loaded."""
        return self.model_class is not None and self.error is None

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
            model_class=result.model_class,
            error=error,
            error_message=result.error_message,
        )