from electric_text.clients.data import UserRequest
from electric_text.providers.model_providers.ollama.ollama_provider_inputs import OllamaProviderInputs
from typing import Dict, Any, Optional

def convert_user_request_to_ollama_inputs(request: UserRequest) -> OllamaProviderInputs:
    # Convert response_model (Type) to format_schema (Dict)
    format_schema: Optional[Dict[str, Any]] = None
    if request.response_model is not None:
        # Check if response_model is a Pydantic model with model_json_schema method
        if hasattr(request.response_model, 'model_json_schema'):
            format_schema = request.response_model.model_json_schema()
        # We don't have a fallback case because we're expecting a Pydantic model
        # If it's not a Pydantic model, we just pass None as format_schema
    
    return OllamaProviderInputs(
        messages=request.messages,
        model=request.model,
        format_schema=format_schema,
    ) 