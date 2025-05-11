from pydantic import BaseModel
from typing import List, Optional

from electric_text.clients.data.client_request import ClientRequest
from electric_text.prompting.functions.create_client_request import (
    create_client_request,
)


class SampleResponseModel(BaseModel):
    content: str
    items: Optional[List[str]] = None


def test_create_client_request_with_defaults():
    """Creates client request with default parameters."""
    request = create_client_request(
        provider_name="test_provider",
        model_name="test_model",
        text_input="Hello, world!",
    )

    assert isinstance(request, ClientRequest)
    assert request.provider_name == "test_provider"
    assert request.model_name == "test_model"
    assert request.prompt.prompt == "Hello, world!"
    assert len(request.prompt.system_message) == 1
    assert request.prompt.system_message[0].text == "You are a helpful assistant."
    assert request.tools is None
    assert request.max_tokens is None
    assert request.response_model is None


def test_create_client_request_with_all_params():
    """Creates client request with all parameters specified."""
    tools = [{"name": "test_tool", "description": "A test tool"}]

    request = create_client_request(
        provider_name="test_provider",
        model_name="test_model",
        text_input="Hello, world!",
        system_message="Custom system message",
        tools=tools,
        max_tokens=100,
        response_model=SampleResponseModel,
    )

    assert isinstance(request, ClientRequest)
    assert request.provider_name == "test_provider"
    assert request.model_name == "test_model"
    assert request.prompt.prompt == "Hello, world!"
    assert len(request.prompt.system_message) == 1
    assert request.prompt.system_message[0].text == "Custom system message"
    assert request.tools == tools
    assert request.max_tokens == 100
    assert request.response_model == SampleResponseModel


def test_create_client_request_with_custom_system_message():
    """Creates client request with custom system message."""
    request = create_client_request(
        provider_name="test_provider",
        model_name="test_model",
        text_input="Hello, world!",
        system_message="You are a specialized assistant.",
    )

    assert isinstance(request, ClientRequest)
    assert len(request.prompt.system_message) == 1
    assert request.prompt.system_message[0].text == "You are a specialized assistant."
