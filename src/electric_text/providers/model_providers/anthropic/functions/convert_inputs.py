from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.anthropic.data.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)
from electric_text.providers.model_providers.anthropic.functions.convert_tools import (
    convert_tools,
)


def convert_provider_inputs(
    request: ProviderRequest,
) -> AnthropicProviderInputs:
    """Convert a ProviderRequest to an AnthropicProviderInputs instance.

    Args:
        request: The ProviderRequest to convert

    Returns:
        AnthropicProviderInputs instance
    """
    messages = convert_prompt_to_messages(
        system_messages=request.system_messages, prompt_text=request.prompt_text
    )

    structured_prefill = request.has_custom_output_schema

    # Convert tools from the standard format to Anthropic's format
    anthropic_tools = convert_tools(request.tools)

    return AnthropicProviderInputs(
        messages=messages,
        model=request.model_name,
        structured_prefill=structured_prefill,
        max_tokens=request.max_tokens,
        tools=anthropic_tools,
    )
