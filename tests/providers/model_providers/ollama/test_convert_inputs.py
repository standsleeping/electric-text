from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from electric_text.clients.data import UserRequest
from electric_text.providers.model_providers.ollama.convert_inputs import (
    convert_user_request_to_ollama_inputs,
)
from electric_text.providers.model_providers.ollama.ollama_provider_inputs import (
    OllamaProviderInputs,
)


# Test Pydantic model
class SampleResponseModel(BaseModel):
    name: str
    age: int
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


def test_convert_without_response_model():
    """Test conversion of UserRequest to OllamaProviderInputs without response_model."""
    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(provider_name="ollama", messages=messages, model="test-model")

    result = convert_user_request_to_ollama_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.format_schema is None


def test_convert_with_pydantic_response_model():
    """Test conversion of UserRequest to OllamaProviderInputs with a Pydantic response_model."""
    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(
        provider_name="ollama",
        messages=messages,
        model="test-model",
        response_model=SampleResponseModel,
    )

    result = convert_user_request_to_ollama_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.format_schema is not None
    assert isinstance(result.format_schema, dict)

    # Verify schema structure
    schema = result.format_schema
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "age" in schema["properties"]
    assert "tags" in schema["properties"]
    assert "metadata" in schema["properties"]
    assert schema["type"] == "object"


def test_convert_with_none_response_model():
    """Test conversion of UserRequest to OllamaProviderInputs with response_model=None."""
    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(
        provider_name="ollama",
        messages=messages,
        model="test-model",
        response_model=None,
    )

    result = convert_user_request_to_ollama_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.format_schema is None
