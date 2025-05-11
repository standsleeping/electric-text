from pydantic import BaseModel

from electric_text.providers.data.user_request import UserRequest
from electric_text.providers.model_providers.openai.convert_inputs import (
    convert_user_request_to_provider_inputs,
)
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)


def test_convert_basic_request():
    """Test conversion of basic UserRequest to OpenAIProviderInputs."""
    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(provider_name="openai", messages=messages, model="test-model")

    result = convert_user_request_to_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"


def test_convert_with_response_model():
    """Test conversion of UserRequest with response_model to OpenAIProviderInputs."""
    # The OpenAI converter doesn't currently use response_model, but the test
    # ensures it handles the parameter without errors

    class ExampleModel(BaseModel):
        name: str
        value: int

    messages = [{"role": "user", "content": "Hello"}]
    request = UserRequest(
        provider_name="openai",
        messages=messages,
        model="test-model",
        response_model=ExampleModel,
    )

    result = convert_user_request_to_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert result.messages == messages
    assert result.model == "test-model"
