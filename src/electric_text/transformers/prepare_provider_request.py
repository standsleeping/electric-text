"""Main entry point for request transformation."""

from typing import Any, Dict, List, Optional, Type

from electric_text.transformers.compose_transformers import compose_transformers
from electric_text.transformers.prefill_transformer import prefill_transformer
from electric_text.transformers.structured_output_transformer import structured_output_transformer


def prepare_provider_request(
    messages: List[Dict[str, str]],
    model: str,
    response_model: Optional[Type[Any]] = None,
    provider_name: str = "",
    prefill_content: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prepare a provider-specific request by applying all relevant transformers.

    This is the main entry point for transforming generic requests to provider-specific ones.

    Args:
        messages: The list of conversation messages
        model: The model ID/name to use
        response_model: Optional model type for structured output
        provider_name: Name of the provider
        prefill_content: Optional content to prefill the model with

    Returns:
        Transformed request with all provider-specific parameters
    """
    # Create base request dictionary
    base_request = {
        "messages": messages,
        "model": model,
    }
    
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
