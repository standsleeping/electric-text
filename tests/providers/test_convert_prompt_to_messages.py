import pytest
from electric_text.providers.functions.convert_prompt_to_messages import (
    convert_prompt_to_messages,
)


def test_convert_prompt_to_messages_minimal():
    """Test convert_prompt_to_messages with minimal input."""
    system_messages = ["You are a helpful assistant."]
    prompt_text = "What's the weather like today?"

    messages = convert_prompt_to_messages(system_messages, prompt_text)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_prompt_to_messages_multiple_system_messages():
    """Test convert_prompt_to_messages with multiple system messages."""
    system_messages = [
        "You are a helpful assistant.",
        "Always be polite.",
    ]
    prompt_text = "What's the weather like today?"

    messages = convert_prompt_to_messages(system_messages, prompt_text)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "Always be polite."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_prompt_to_messages_no_system_message():
    """Test convert_prompt_to_messages with no system message raises error."""
    system_messages = None
    prompt_text = "Hello"

    with pytest.raises(ValueError) as exc_info:
        convert_prompt_to_messages(system_messages, prompt_text)

    assert "System message is required" in str(exc_info.value)


def test_convert_prompt_to_messages_empty_system_message():
    """Test convert_prompt_to_messages with empty system message list."""
    system_messages = []
    prompt_text = "Hello"

    # Empty list is valid, should not raise an error
    messages = convert_prompt_to_messages(system_messages, prompt_text)

    # Should only have the user message since system_message is empty
    expected_messages = [
        {"role": "user", "content": "Hello"},
    ]

    assert messages == expected_messages
