from dataclasses import dataclass
from typing import Optional, Dict, Any

from electric_text.clients.functions.load_validation_model import load_validation_model
from electric_text.clients.data.model_load_result import ModelLoadResult
from electric_text.clients.data.model_load_error import ModelLoadError
from electric_text.clients.data.model_result import ModelResult


@dataclass
class PromptConfig:
    """Model representing a prompt configuration loaded from config files."""

    name: str
    """Name of the prompt"""

    description: str
    """Description of what the prompt does"""

    system_message_path: str
    """Path to the text file containing the system message"""

    model_path: Optional[str] = None
    """Path to Python file containing a validation model for response validation"""

    def get_system_message(self) -> str:
        """Load the system message from the specified path."""
        with open(self.system_message_path, "r") as f:
            return f.read()

    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load the schema from the validation model in the specified Python file.

        Returns:
            Optional[Dict[str, Any]]: The JSON schema derived from the validation model,
                                      or None if no model_path is specified or an error occurred.
        """
        result = self.get_model_class()
        if result.is_valid and result.model_class:
            schema = result.model_class.model_json_schema()
            if isinstance(schema, dict):
                return schema

        return None

    def get_model_class(self) -> ModelResult:
        """
        Get the validation model class from the Python file if it exists.

        Returns:
            ModelResult: Result of loading the model class, with error information if applicable.
        """
        if not self.model_path:
            return ModelResult(
                error=ModelLoadError.NOT_FOUND,
                error_message="No model path specified",
            )

        load_result: ModelLoadResult = load_validation_model(self.model_path)

        return ModelResult.from_load_result(load_result)
