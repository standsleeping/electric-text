"""Transformer for structured output capabilities."""

from typing import Any, Dict

from electric_text.capabilities import ProviderCapability, ProviderCapabilities


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
