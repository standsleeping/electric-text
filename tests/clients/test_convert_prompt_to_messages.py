import pytest
from electric_text.clients import convert_prompt_to_messages
from electric_text.clients.data.prompt import Prompt
from electric_text.clients.data.template_fragment import TemplateFragment


def test_convert_prompt_to_messages_minimal():
    """Test convert_prompt_to_messages with minimal input."""
    system_message = [TemplateFragment(text="You are a helpful assistant.")]
    user_message = "What's the weather like today?"
    prompt = Prompt(system_message=system_message, prompt=user_message)

    messages = convert_prompt_to_messages(prompt)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_prompt_to_messages_multiple_system_fragments():
    """Test convert_prompt_to_messages with multiple system message fragments."""
    system_message = [
        TemplateFragment(text="You are a helpful assistant."),
        TemplateFragment(text="Always be polite."),
    ]
    user_message = "What's the weather like today?"
    prompt = Prompt(system_message=system_message, prompt=user_message)

    messages = convert_prompt_to_messages(prompt)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "Always be polite."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_prompt_to_messages_no_system_message():
    """Test convert_prompt_to_messages with no system message raises error."""
    prompt = Prompt(system_message=None, prompt="Hello")

    with pytest.raises(ValueError) as exc_info:
        convert_prompt_to_messages(prompt)

    assert "System message is required" in str(exc_info.value)


def test_convert_prompt_to_messages_empty_system_message():
    """Test convert_prompt_to_messages with empty system message list."""
    prompt = Prompt(system_message=[], prompt="Hello")

    # Empty list is valid, should not raise an error
    messages = convert_prompt_to_messages(prompt)

    # Should only have the user message since system_message is empty
    expected_messages = [
        {"role": "user", "content": "Hello"},
    ]

    assert messages == expected_messages
