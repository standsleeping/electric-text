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


def test_convert_with_output_schema():
    """Test conversion of ProviderRequest with output_schema to OpenAIProviderInputs."""
    # The OpenAI converter doesn't currently use output_schema, but the test
    # ensures it handles the parameter without errors

    class ExampleModel(BaseModel):
        name: str
        value: int

    request = ProviderRequest(
        provider_name="openai",
        prompt_text="Hello",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        output_schema=ExampleModel,
        has_custom_output_schema=True,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"


def test_convert_with_tools():
    """Test conversion of ProviderRequest with tools to OpenAIProviderInputs."""
    # Standard tools format
    standard_tools = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                },
                "required": ["location"],
            },
        }
    ]

    # Expected OpenAI format (what the conversion should produce)
    expected_openai_tools = [
        {
            "type": "function",
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                },
                "required": ["location"],
            },
        }
    ]

    request = ProviderRequest(
        provider_name="openai",
        prompt_text="What's the weather?",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        tools=standard_tools,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.tools == expected_openai_tools


def test_convert_with_multiple_tools():
    """Test conversion of ProviderRequest with multiple tools to OpenAIProviderInputs."""
    # Standard tools format with multiple tools
    standard_tools = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                },
                "required": ["location"],
            },
        },
        {
            "name": "get_forecast",
            "description": "Get the weather forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast",
                        "minimum": 1,
                        "maximum": 7,
                    },
                },
                "required": ["location", "days"],
            },
        },
    ]

    # Expected OpenAI format for multiple tools
    expected_openai_tools = [
        {
            "type": "function",
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Omaha, NE",
                    },
                },
                "required": ["location"],
            },
        },
        {
            "type": "function",
            "name": "get_forecast",
            "description": "Get the weather forecast for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast",
                        "minimum": 1,
                        "maximum": 7,
                    },
                },
                "required": ["location", "days"],
            },
        },
    ]

    request = ProviderRequest(
        provider_name="openai",
        prompt_text="What's the weather forecast?",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        tools=standard_tools,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.tools == expected_openai_tools


def test_convert_with_no_tools():
    """Test conversion of ProviderRequest with no tools to OpenAIProviderInputs."""
    request = ProviderRequest(
        provider_name="openai",
        prompt_text="Hello there",
        model_name="test-model",
        system_messages=["You are a helpful assistant"],
        tools=None,
    )

    result = convert_provider_inputs(request)

    assert isinstance(result, OpenAIProviderInputs)
    assert len(result.messages) == 2  # system message + user message
    assert result.model == "test-model"
    assert result.tools is None
