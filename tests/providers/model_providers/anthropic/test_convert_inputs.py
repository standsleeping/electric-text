from pydantic import BaseModel

from electric_text.clients.data import UserRequest
from electric_text.providers.model_providers.anthropic.convert_inputs import (
    convert_user_request_to_anthropic_inputs,
)
from electric_text.providers.model_providers.anthropic.anthropic_provider_inputs import (
    AnthropicProviderInputs,
)


def test_convert_basic_request():
    """Test conversion of basic UserRequest to AnthropicProviderInputs."""
    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(
        provider_name="anthropic", messages=messages, model="test-model"
    )

    result = convert_user_request_to_anthropic_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.prefill_content is None
    assert result.structured_prefill is True


def test_convert_with_prefill():
    """Test conversion of UserRequest with prefill to AnthropicProviderInputs."""
    messages = [{"role": "user", "content": "Hello"}]
    prefill = "This is a prefill"
    request = UserRequest(
        provider_name="anthropic",
        messages=messages,
        model="test-model",
        prefill_content=prefill,
    )

    result = convert_user_request_to_anthropic_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.prefill_content == prefill
    assert result.structured_prefill is True


def test_convert_with_response_model():
    """Test conversion of UserRequest with response_model to AnthropicProviderInputs."""
    # The Anthropic converter doesn't currently use response_model, but the test
    # ensures it handles the parameter without errors

    class ExampleModel(BaseModel):
        name: str
        value: int

    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(
        provider_name="anthropic",
        messages=messages,
        model="test-model",
        response_model=ExampleModel,
    )

    result = convert_user_request_to_anthropic_inputs(request)

    assert isinstance(result, AnthropicProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
    assert result.prefill_content is None
    assert result.structured_prefill is True
