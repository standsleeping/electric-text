"""Type definitions for the transformers package."""

from typing import Any, Dict, Callable, TypeVar

# Type for any model class
ModelType = TypeVar("ModelType")

# Type for transformer functions with keyword arguments
TransformerFn = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
