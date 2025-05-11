"""Tests for the command-line interface."""

from electric_text.cli.functions.parse_args import parse_args
from electric_text.cli.data.system_input import SystemInput


def test_parse_args() -> None:
    """Test argument parsing with SystemInput return type."""
    system_input = parse_args(["hello"])
    assert isinstance(system_input, SystemInput)
    assert system_input.text_input == "hello"
    assert system_input.log_level == "ERROR"
    assert system_input.max_tokens is None
    assert system_input.provider_name == "ollama"
    assert system_input.model_name == "llama3.1:8b"

    system_input = parse_args(["hello", "--log-level", "DEBUG"])
    assert system_input.text_input == "hello"
    assert system_input.log_level == "DEBUG"
    assert system_input.max_tokens is None

    system_input = parse_args(["hello", "--max-tokens", "500"])
    assert system_input.text_input == "hello"
    assert system_input.max_tokens == 500

    system_input = parse_args(["hello", "-mt", "1000"])
    assert system_input.text_input == "hello"
    assert system_input.max_tokens == 1000

    system_input = parse_args(
        [
            "hello",
            "--model",
            "anthropic:claude-3-7-sonnet-20250219",
        ]
    )

    assert system_input.provider_name == "anthropic"
    assert system_input.model_name == "claude-3-7-sonnet-20250219"

    system_input = parse_args(["hello", "--prompt-name", "poetry", "--stream"])
    assert system_input.prompt_name == "poetry"
    assert system_input.stream is True
