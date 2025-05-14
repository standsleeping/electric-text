from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.ollama.ollama_provider_inputs import (
    OllamaProviderInputs,
)
from typing import Dict, Any, Optional
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)


def convert_provider_inputs(
    request: ProviderRequest,
) -> OllamaProviderInputs:
    """Convert a ProviderRequest to an OllamaProviderInputs instance.

    Args:
        request: The ProviderRequest to convert

    Returns:
        OllamaProviderInputs instance
    """
    # Convert response_model (Type) to format_schema (Dict)
    format_schema: Optional[Dict[str, Any]] = None

    if request.response_model is not None:
        # Check if response_model is a Pydantic model with model_json_schema method
        if hasattr(request.response_model, "model_json_schema"):
            format_schema = request.response_model.model_json_schema()
        # We don't have a fallback case because we're expecting a Pydantic model
        # If it's not a Pydantic model, we just pass None as format_schema

    messages = convert_prompt_to_messages(
        system_messages=request.system_messages,
        prompt_text=request.prompt_text,
    )

    return OllamaProviderInputs(
        messages=messages,
        model=request.model_name,
        format_schema=format_schema,
    )
