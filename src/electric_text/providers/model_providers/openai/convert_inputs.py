from electric_text.responses import UserRequest
from electric_text.providers.model_providers.openai.openai_provider_inputs import OpenAIProviderInputs

def convert_user_request_to_openai_inputs(request: UserRequest) -> OpenAIProviderInputs:
    return OpenAIProviderInputs(
        messages=request.messages,
        model=request.model,
    ) 