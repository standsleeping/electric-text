from electric_text.responses import UserRequest
from electric_text.providers.model_providers.anthropic.anthropic_provider_inputs import AnthropicProviderInputs

def convert_user_request_to_anthropic_inputs(request: UserRequest) -> AnthropicProviderInputs:
    return AnthropicProviderInputs(
        messages=request.messages,
        model=request.model,
        prefill_content=request.prefill_content,
        structured_prefill=True,
    )