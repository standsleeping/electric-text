from electric_text.responses import UserRequest
from electric_text.providers.model_providers.ollama.ollama_provider_inputs import OllamaProviderInputs

def convert_user_request_to_ollama_inputs(request: UserRequest) -> OllamaProviderInputs:
    return OllamaProviderInputs(
        messages=request.messages,
        model=request.model,
        format_schema=request.response_model,
    ) 