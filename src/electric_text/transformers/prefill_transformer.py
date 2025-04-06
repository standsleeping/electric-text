"""Transformer for prefill capabilities."""

from typing import Any, Dict

from electric_text.capabilities import ProviderCapability, ProviderCapabilities


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
