from electric_text.providers.data.user_request import UserRequest
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)


def convert_user_request_to_provider_inputs(request: UserRequest) -> OpenAIProviderInputs:
    return OpenAIProviderInputs(
        messages=request.messages,
        model=request.model,
    )
