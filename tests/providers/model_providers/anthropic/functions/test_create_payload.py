from electric_text.providers.model_providers.anthropic.functions.create_payload import (
    create_payload,
)


def test_create_payload_basic():
    """Creates payload with basic messages."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "claude-3-sonnet-20240229"

    default_model = "claude-3-opus-20240229"

    stream = False

    payload = create_payload(model, default_model, messages, stream)

    assert payload["model"] == model
    assert payload["messages"] == messages
    assert payload["stream"] is False
    assert payload["max_tokens"] == 4096  # Default value
    assert "tools" not in payload


def test_create_payload_with_max_tokens():
    """Creates payload with custom max tokens."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "claude-3-sonnet-20240229"

    default_model = "claude-3-opus-20240229"

    stream = False

    max_tokens = 1000

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        max_tokens=max_tokens,
    )

    assert payload["model"] == model
    assert payload["messages"] == messages
    assert payload["stream"] is False
    assert payload["max_tokens"] == max_tokens
    assert "tools" not in payload


def test_create_payload_with_tools():
    """Creates payload with tools."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "claude-3-sonnet-20240229"

    default_model = "claude-3-opus-20240229"

    stream = False

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

    payload = create_payload(model, default_model, messages, stream, tools=tools)

    assert payload["model"] == model
    assert payload["messages"] == messages
    assert payload["stream"] is False
    assert payload["max_tokens"] == 4096  # Default value
    assert payload["tools"] == tools


def test_create_payload_with_empty_tools():
    """Creates payload with empty tools list (should omit tools field)."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "claude-3-sonnet-20240229"

    default_model = "claude-3-opus-20240229"

    stream = False

    tools = []

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        tools=tools,
    )

    assert payload["model"] == model
    assert payload["messages"] == messages
    assert payload["stream"] is False
    assert payload["max_tokens"] == 4096  # Default value
    assert "tools" not in payload


def test_create_payload_with_tools_and_max_tokens():
    """Creates payload with both tools and max_tokens."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "claude-3-sonnet-20240229"

    default_model = "claude-3-opus-20240229"

    stream = False

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

    max_tokens = 1000

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        max_tokens=max_tokens,
        tools=tools,
    )

    assert payload["model"] == model
    assert payload["messages"] == messages
    assert payload["stream"] is False
    assert payload["max_tokens"] == max_tokens
    assert payload["tools"] == tools
