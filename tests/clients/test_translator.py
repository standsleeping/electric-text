import pytest
from electric_text.clients import (
    build_simple_prompt,
    convert_to_llm_messages,
    Prompt,
    TemplateFragment,
)

def test_build_simple_prompt():
    system_message = "You are a helpful assistant."
    user_message = "What's the weather like today?"

    prompt = build_simple_prompt(system_message, user_message)

    assert isinstance(prompt, Prompt)
    assert len(prompt.system_message) == 1
    assert isinstance(prompt.system_message[0], TemplateFragment)
    assert prompt.system_message[0].text == system_message
    assert prompt.prompt == user_message


def test_convert_to_llm_messages():
    system_message = [TemplateFragment(text="You are a helpful assistant.")]
    user_message = "What's the weather like today?"
    prompt = Prompt(system_message=system_message, prompt=user_message)

    messages = convert_to_llm_messages(prompt)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_to_llm_messages_multiple_system_fragments():
    system_message = [
        TemplateFragment(text="You are a helpful assistant."),
        TemplateFragment(text="Always be polite."),
    ]
    user_message = "What's the weather like today?"
    prompt = Prompt(system_message=system_message, prompt=user_message)

    messages = convert_to_llm_messages(prompt)

    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "system", "content": "Always be polite."},
        {"role": "user", "content": "What's the weather like today?"},
    ]

    assert messages == expected_messages


def test_convert_to_llm_messages_no_system_message():
    prompt = Prompt(system_message=None, prompt="Hello")

    with pytest.raises(ValueError) as context:
        convert_to_llm_messages(prompt)

    assert context.value.args[0] == "System message is required"
