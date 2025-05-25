from typing import Dict, Any, List

from electric_text.providers.model_providers.openai.functions.create_payload import (
    create_payload,
)


def test_create_payload_includes_tools():
    """Creates payload with tools when tools are provided."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What's the weather?"},
    ]

    tools: List[Dict[str, Any]] = [
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

    payload = create_payload(
        model="test-model",
        default_model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        tools=tools,
    )

    assert payload["tools"] == tools


def test_create_payload_omits_tools_when_none_provided():
    """Omits tools from payload when no tools are provided."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    payload = create_payload(
        model="test-model",
        default_model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )

    assert "tools" not in payload


def test_create_payload_includes_tools_with_format_schema():
    """Includes both tools and format_schema in payload when both are provided."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What's the weather?"},
    ]

    tools: List[Dict[str, Any]] = [
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

    format_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        },
        "required": ["name", "age"],
    }

    payload = create_payload(
        model="test-model",
        default_model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
        format_schema=format_schema,
        tools=tools,
    )

    assert payload["tools"] == tools
    assert "text" in payload
