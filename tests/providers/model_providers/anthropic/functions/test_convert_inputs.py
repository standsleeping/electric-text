from pydantic import BaseModel

from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.anthropic.functions.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.model_providers.anthropic.data.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)


def test_convert_basic_request():
    """Test conversion of basic ProviderRequest to AnthropicProviderInputs."""
    request = ProviderRequest(
        provider_name="anthropic",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.structured_prefill is False
    assert result.max_tokens is None
    assert result.tools is None


def test_convert_with_prefill():
    """Test conversion of ProviderRequest with prefill to AnthropicProviderInputs."""

    prefill = "This is a prefill"  # TODO: come back to this

    request = ProviderRequest(
        provider_name="anthropic",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        max_tokens=None,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.structured_prefill is False
    assert result.max_tokens is None
    assert result.tools is None


def test_convert_with_max_tokens():
    """Test conversion of ProviderRequest with max_tokens to AnthropicProviderInputs."""
    max_tokens = 1000
    request = ProviderRequest(
        provider_name="anthropic",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        max_tokens=max_tokens,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.structured_prefill is False
    assert result.max_tokens == max_tokens
    assert result.tools is None


def test_convert_with_response_model():
    """Test conversion of ProviderRequest with response_model to AnthropicProviderInputs."""
    # The Anthropic converter doesn't currently use response_model, but the test
    # ensures it handles the parameter without errors

    class ExampleModel(BaseModel):
        name: str
        value: int

    request = ProviderRequest(
        provider_name="anthropic",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        response_model=ExampleModel,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.structured_prefill is True
    assert result.max_tokens is None
    assert result.tools is None


def test_convert_with_tools():
    """Test conversion of ProviderRequest with tools to AnthropicProviderInputs."""
    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    ]

    request = ProviderRequest(
        provider_name="anthropic",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        tools=tools,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.structured_prefill is False
    assert result.max_tokens is None
    assert result.tools == tools


