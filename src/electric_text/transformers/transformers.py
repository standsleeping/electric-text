"""Request transformers for adapting generic client requests to provider-specific formats.

This module contains pure functions that transform request parameters based on
provider capabilities, following functional programming principles.
"""

from typing import Any, Dict, Optional, Type, Callable, TypeVar

from electric_text.capabilities import ProviderCapability, ProviderCapabilities

# Type for any model class
ModelType = TypeVar("ModelType")

# Type for transformer functions with keyword arguments
TransformerFn = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


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


def structured_output_transformer(
    request: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Transform a request to include structured output parameters if applicable.

    Args:
        request: The base request dictionary
        context: Context containing response_model and provider_name

    Returns:
        Transformed request with provider-specific structured output parameters
    """
    response_model = context.get("response_model")
    provider_name = context.get("provider_name", "")

    if not response_model:
        return request.copy()

    # New dict to ensure immutability
    transformed = request.copy()

    # Get provider capabilities
    capabilities = ProviderCapabilities(provider_name)

    # Only proceed if the provider supports structured output
    if capabilities.supports(ProviderCapability.STRUCTURED_OUTPUT):
        # Get capability parameters
        capability_params = capabilities.get_capability_params(
            ProviderCapability.STRUCTURED_OUTPUT
        )

        if capability_params:
            param_name = capability_params.get("param")
            schema_method = capability_params.get("schema_method")
            fixed_value = capability_params.get("value")

            # Handle fixed value capability (like Anthropic's structured_prefill)
            if param_name and fixed_value is not None:
                transformed[param_name] = fixed_value

            # Handle schema-based capability (like Ollama's format_schema)
            elif (
                param_name and schema_method and hasattr(response_model, schema_method)
            ):
                schema_fn = getattr(response_model, schema_method)
                transformed[param_name] = schema_fn()

    return transformed


def prefill_transformer(
    request: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Transform a request to include prefill parameters if applicable.

    This handles provider-specific prefill capabilities, including structured prefill
    flags that may be needed alongside structured output parameters.

    Args:
        request: The base request dictionary
        context: Context containing provider_name and prefill_content (optional)

    Returns:
        Transformed request with provider-specific prefill parameters
    """
    provider_name = context.get("provider_name", "")
    prefill_content = context.get("prefill_content")
    response_model = context.get("response_model")

    # New dict to ensure immutability
    transformed = request.copy()

    # Only add prefill parameters if we have a structured output request
    # or explicit prefill content
    if not (response_model or prefill_content):
        return transformed

    # Get provider capabilities
    capabilities = ProviderCapabilities(provider_name)

    # Only proceed if the provider supports prefill capability
    if capabilities.supports(ProviderCapability.PREFILL):
        # Get capability parameters
        capability_params = capabilities.get_capability_params(
            ProviderCapability.PREFILL
        )

        if capability_params:
            # For structured output with response_model, add the structured_prefill flag
            if response_model and "structured_param" in capability_params:
                structured_param = capability_params.get("structured_param", "")
                if structured_param:  # Ensure we have a valid string parameter name
                    structured_value = capability_params.get("structured_value", True)
                    transformed[structured_param] = structured_value

            # For explicit prefill_content, add the content parameter
            if prefill_content and "param" in capability_params:
                param_name = capability_params.get("param", "")
                if param_name:  # Ensure we have a valid string parameter name
                    transformed[param_name] = prefill_content

    return transformed


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
