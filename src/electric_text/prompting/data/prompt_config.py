import importlib.util
import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any, Type, cast


class ModelLoadError(Enum):
    NOT_FOUND = auto()
    IMPORT_ERROR = auto()
    NO_MODEL = auto()
    OTHER = auto()


@dataclass
class ModelResult:
    """Result of loading a Pydantic model from a Python file."""
    model_class: Optional[Type[Any]] = None
    error: Optional[ModelLoadError] = None
    error_message: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Returns True if a valid model was loaded."""
        return self.model_class is not None and self.error is None


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
    """Path to Python file containing a Pydantic model for response validation"""

    def get_system_message(self) -> str:
        """Load the system message from the specified path."""
        with open(self.system_message_path, "r") as f:
            return f.read()

    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load the schema from the Pydantic model in the specified Python file.
        
        Returns:
            Optional[Dict[str, Any]]: The JSON schema derived from the Pydantic model,
                                     or None if no model_path is specified or an error occurred.
        """
        result = self.get_model_class()
        if result.is_valid and result.model_class:
            schema = result.model_class.model_json_schema()
            if isinstance(schema, dict):
                return schema
            return None
        return None

    def get_model_class(self) -> ModelResult:
        """
        Get the Pydantic model class from the Python file if it exists.
        
        Returns:
            ModelResult: Result of loading the model class, with error information if applicable.
        """
        if not self.model_path:
            return ModelResult(error=ModelLoadError.NOT_FOUND, error_message="No model path specified")
            
        try:
            # Import the module dynamically
            spec = importlib.util.spec_from_file_location("schema_module", self.model_path)
            if spec is None or spec.loader is None:
                return ModelResult(
                    error=ModelLoadError.IMPORT_ERROR,
                    error_message=f"Could not load module from {self.model_path}"
                )
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["schema_module"] = module
            spec.loader.exec_module(module)
            
            # Find the first class that inherits from BaseModel
            from pydantic import BaseModel
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) 
                    and issubclass(attr, BaseModel) 
                    and attr != BaseModel
                ):
                    return ModelResult(model_class=attr)
            
            return ModelResult(
                error=ModelLoadError.NO_MODEL,
                error_message=f"No Pydantic model found in {self.model_path}"
            )
        
        except Exception as e:
            return ModelResult(
                error=ModelLoadError.OTHER,
                error_message=f"Error loading Pydantic model from {self.model_path}: {str(e)}"
            )
