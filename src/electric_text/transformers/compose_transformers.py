"""Function composition for transformer functions."""

from typing import Any, Dict

from electric_text.transformers.types import TransformerFn


def compose_transformers(*transformers: TransformerFn) -> TransformerFn:
    """
    Compose multiple transformer functions into a single function.

    Args:
        *transformers: Transformer functions to compose

    Returns:
        Function that applies all transformers in sequence
    """

    def composed(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        result = request.copy()  # Ensure immutability
        for transformer in transformers:
            result = transformer(result, context)
        return result

    return composed
