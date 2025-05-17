from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.anthropic.data.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)


def convert_provider_inputs(
    request: ProviderRequest,
) -> AnthropicProviderInputs:
    messages = convert_prompt_to_messages(
        system_messages=request.system_messages,
        prompt_text=request.prompt_text
    )

    if request.response_model:
        structured_prefill = True
    else:
        structured_prefill = False

    return AnthropicProviderInputs(
        messages=messages,
        model=request.model_name,
        structured_prefill=structured_prefill,
        max_tokens=request.max_tokens,
    )
