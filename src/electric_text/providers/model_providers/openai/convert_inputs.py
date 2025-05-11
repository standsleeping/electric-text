from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)


def convert_provider_inputs(
    request: ProviderRequest,
) -> OpenAIProviderInputs:

    messages = convert_prompt_to_messages(
        system_messages=request.system_messages,
        prompt_text=request.prompt_text
    )

    return OpenAIProviderInputs(
        messages=messages,
        model=request.model_name,
    )
