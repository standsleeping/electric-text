"""Tests for the SystemInput dataclass."""

from electric_text.cli.data.system_input import SystemInput


def test_system_input_defaults():
    """Test SystemInput with default values."""
    system_input = SystemInput(
        text_input="hello",
        provider_name="test_provider",
        model_name="test_model",
    )

    assert system_input.text_input == "hello"
    assert system_input.provider_name == "test_provider"
    assert system_input.model_name == "test_model"
    assert system_input.log_level == "ERROR"
    assert system_input.api_key is None
    assert system_input.max_tokens is None
    assert system_input.prompt_name is None
    assert system_input.stream is False
    assert system_input.tool_boxes is None


def test_system_input_all_values():
    """Test SystemInput with all values specified."""
    system_input = SystemInput(
        text_input="test input",
        provider_name="anthropic",
        model_name="claude-3-7-sonnet-20250219",
        log_level="DEBUG",
        api_key="test_api_key",
        max_tokens=500,
        prompt_name="poetry",
        stream=True,
        tool_boxes="box1,box2",
    )

    assert system_input.text_input == "test input"
    assert system_input.provider_name == "anthropic"
    assert system_input.model_name == "claude-3-7-sonnet-20250219"
    assert system_input.log_level == "DEBUG"
    assert system_input.api_key == "test_api_key"
    assert system_input.max_tokens == 500
    assert system_input.prompt_name == "poetry"
    assert system_input.stream is True
    assert system_input.tool_boxes == "box1,box2"
