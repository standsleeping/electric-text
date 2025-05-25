from electric_text.providers.model_providers.openai.functions.create_payload import (
    create_payload,
)


def test_create_payload_basic():
    """Creates payload with basic messages."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

    stream = False

    payload = create_payload(model, default_model, messages, stream)

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" not in payload
    assert "tools" not in payload


def test_create_payload_with_default_model():
    """Creates payload using default model when model is None."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = None

    default_model = "gpt-3.5-turbo"

    stream = True

    payload = create_payload(model, default_model, messages, stream)

    assert payload["model"] == default_model
    assert payload["input"] == messages
    assert payload["stream"] is True
    assert "text" not in payload
    assert "tools" not in payload


def test_create_payload_with_format_schema():
    """Creates payload with format schema."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

    stream = False

    format_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        format_schema=format_schema,
    )

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" in payload  # set_text_format should be called
    assert "tools" not in payload


def test_create_payload_with_format_schema_non_strict():
    """Creates payload with format schema and non-strict validation."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

    stream = False

    format_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        format_schema=format_schema,
        strict_schema=False,
    )

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" in payload  # set_text_format should be called
    assert "tools" not in payload


def test_create_payload_with_tools():
    """Creates payload with tools."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

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
                        "description": "The city and state, e.g. Chicago, IL",
                    }
                },
                "required": ["location"],
            },
        }
    ]

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        tools=tools,
    )

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" not in payload
    assert payload["tools"] == tools


def test_create_payload_with_empty_tools():
    """Creates payload with empty tools list (should still include tools field)."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

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
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" not in payload
    assert "tools" not in payload  # Empty list is falsy


def test_create_payload_with_none_tools():
    """Creates payload with None tools (should omit tools field)."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

    stream = False

    tools = None

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        tools=tools,
    )

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is False
    assert "text" not in payload
    assert "tools" not in payload


def test_create_payload_with_all_options():
    """Creates payload with all options."""
    messages = [
        {"role": "user", "content": "Hello"},
    ]

    model = "gpt-4o-mini"

    default_model = "gpt-3.5-turbo"

    stream = True

    format_schema = {
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    }

    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. Chicago, IL",
                    }
                },
                "required": ["location"],
            },
        }
    ]

    payload = create_payload(
        model,
        default_model,
        messages,
        stream,
        format_schema=format_schema,
        strict_schema=False,
        tools=tools,
    )

    assert payload["model"] == model
    assert payload["input"] == messages
    assert payload["stream"] is True
    assert "text" in payload  # set_text_format should be called
    assert payload["tools"] == tools
