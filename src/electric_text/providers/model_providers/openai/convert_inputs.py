from typing import Optional, Dict, Any
from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)
from electric_text.providers.model_providers.openai.functions.convert_tools import (
    convert_tools as convert_tools_impl,
)


def convert_provider_inputs(
    request: ProviderRequest,
) -> OpenAIProviderInputs:
    """Convert a ProviderRequest to an OpenAIProviderInputs instance.

    Args:
        request: The ProviderRequest to convert

    Returns:
        OpenAIProviderInputs instance
    """
    # Convert output_schema (Type) to format_schema (Dict)
    format_schema: Optional[Dict[str, Any]] = None

    if request.has_custom_output_schema and request.output_schema is not None:
        # Check if output_schema is a Pydantic model with model_json_schema method
        if hasattr(request.output_schema, "model_json_schema"):
            format_schema = request.output_schema.model_json_schema()

    messages = convert_prompt_to_messages(
        system_messages=request.system_messages,
        prompt_text=request.prompt_text,
    )

    # Convert tools from the standard format to OpenAI's format
    openai_tools = convert_tools_impl(request.tools)

    return OpenAIProviderInputs(
        messages=messages,
        model=request.model_name,
        format_schema=format_schema,
        tools=openai_tools,
    )
