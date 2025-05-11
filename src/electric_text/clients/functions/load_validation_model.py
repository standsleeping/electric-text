import sys
import importlib.util
from electric_text.clients.data.validation_model import ValidationModel, ModelLoadResult


def load_validation_model(model_path: str) -> ModelLoadResult:
    """
    Load a validation model class from a Python file.

    Args:
        model_path: Path to the Python file containing the validation model.

    Returns:
        ModelLoadResult: Result of loading the model class, with error information if applicable.
    """
    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("schema_module", model_path)
        if spec is None or spec.loader is None:
            return ModelLoadResult(
                error="IMPORT_ERROR",
                error_message=f"Could not load module from {model_path}",
            )

        module = importlib.util.module_from_spec(spec)
        sys.modules["schema_module"] = module
        spec.loader.exec_module(module)

        # Find the first class that implements the ValidationModel protocol
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, ValidationModel)
                and attr.__name__ != "ValidationModel"
                and attr.__module__ == "schema_module"
            ):
                return ModelLoadResult(model_class=attr)

        return ModelLoadResult(
            error="NO_MODEL", error_message=f"No validation model found in {model_path}"
        )

    except Exception as e:
        return ModelLoadResult(
            error="OTHER",
            error_message=f"Error loading validation model from {model_path}: {str(e)}",
        )
