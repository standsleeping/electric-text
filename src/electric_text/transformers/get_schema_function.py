"""Functions for working with schema functions."""

from typing import Any, Dict, Optional, Type, Callable


def get_schema_function(
    model_type: Type[Any], schema_method_name: str = "model_json_schema"
) -> Optional[Callable[[], Dict[str, Any]]]:
    """
    Get the schema function from a model type if available.

    Args:
        model_type: The model type to get the schema from
        schema_method_name: Name of the method that returns the schema

    Returns:
        Optional callable that returns a schema dict
    """
    if hasattr(model_type, schema_method_name):
        schema_fn: Callable[[], Dict[str, Any]] = getattr(
            model_type, schema_method_name
        )
        return schema_fn
    return None
