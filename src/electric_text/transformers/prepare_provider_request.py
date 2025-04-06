"""Main entry point for request transformation."""

from typing import Any, Dict, Optional, Type

from electric_text.transformers.compose_transformers import compose_transformers
from electric_text.transformers.prefill_transformer import prefill_transformer
from electric_text.transformers.structured_output_transformer import structured_output_transformer


def prepare_provider_request(
    base_request: Dict[str, Any],
    response_model: Optional[Type[Any]] = None,
    provider_name: str = "",
    prefill_content: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare a provider-specific request by applying all relevant transformers.

    This is the main entry point for transforming generic requests to provider-specific ones.

    Args:
        base_request: The base request parameters
        response_model: Optional model type for structured output
        provider_name: Name of the provider
        prefill_content: Optional content to prefill the model with

    Returns:
        Transformed request with all provider-specific parameters
    """
    # Create context dict with all parameters
    context = {
        "response_model": response_model,
        "provider_name": provider_name,
        "prefill_content": prefill_content,
    }

    # Compose all transformers in sequence
    transform = compose_transformers(
        structured_output_transformer,
        prefill_transformer,
    )

    # Apply transformations
    return transform(base_request, context)
