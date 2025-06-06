from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.ollama.functions.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.model_providers.ollama.data.ollama_provider_inputs import (
    OllamaProviderInputs,
)


# Test Pydantic model
class SampleOutputSchema(BaseModel):
    name: str
    age: int
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


def test_convert_without_output_schema():
    """Test conversion of ProviderRequest to OllamaProviderInputs without output_schema."""

    request = ProviderRequest(
        provider_name="ollama",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.format_schema is None


def test_convert_with_pydantic_output_schema():
    """Test conversion of ProviderRequest to OllamaProviderInputs with a Pydantic output_schema."""

    request = ProviderRequest(
        provider_name="ollama",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        output_schema=SampleOutputSchema,
        has_custom_output_schema=True,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.format_schema is not None
    assert isinstance(result.format_schema, dict)

    # Verify schema structure
    schema = result.format_schema
    assert schema is not None
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "age" in schema["properties"]
    assert "tags" in schema["properties"]
    assert "metadata" in schema["properties"]
    assert schema["type"] == "object"


def test_convert_with_none_output_schema():
    """Test conversion of ProviderRequest to OllamaProviderInputs with output_schema=None."""

    request = ProviderRequest(
        provider_name="ollama",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        output_schema=None,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OllamaProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.format_schema is None
