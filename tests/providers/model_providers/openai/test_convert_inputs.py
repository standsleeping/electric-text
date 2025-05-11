from pydantic import BaseModel

from electric_text.providers.data.provider_request import ProviderRequest
from electric_text.providers.model_providers.openai.convert_inputs import (
    convert_provider_inputs,
)
from electric_text.providers.model_providers.openai.openai_provider_inputs import (
    OpenAIProviderInputs,
)


def test_convert_basic_request():
    """Test conversion of basic ProviderRequest to OpenAIProviderInputs."""
    request = ProviderRequest(
        provider_name="openai",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"


def test_convert_with_response_model():
    """Test conversion of ProviderRequest with response_model to OpenAIProviderInputs."""
    # The OpenAI converter doesn't currently use response_model, but the test
    # ensures it handles the parameter without errors

    class ExampleModel(BaseModel):
        name: str
        value: int

    request = ProviderRequest(
        provider_name="openai",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        response_model=ExampleModel,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
