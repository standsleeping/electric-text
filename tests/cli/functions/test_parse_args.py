"""Tests for the command-line interface."""

from electric_text.cli.functions.parse_args import parse_args
from electric_text.prompting.data.system_input import SystemInput


def test_parse_args() -> None:
    """Test argument parsing returns raw SystemInput and config path."""
    raw_input, config_path = parse_args(["hello"])
    assert isinstance(raw_input, SystemInput)
    assert raw_input.text_input == "hello"
    assert raw_input.log_level == "ERROR"
    assert raw_input.max_tokens is None
    assert raw_input.provider_name == ""  # Not resolved yet
    assert raw_input.model_name == "ollama:llama3.1:8b"  # Raw model string
    assert config_path is None

    raw_input, config_path = parse_args(["hello", "--log-level", "DEBUG"])
    assert raw_input.text_input == "hello"
    assert raw_input.log_level == "DEBUG"
    assert raw_input.max_tokens is None

    raw_input, config_path = parse_args(["hello", "--max-tokens", "500"])
    assert raw_input.text_input == "hello"
    assert raw_input.max_tokens == 500

    raw_input, config_path = parse_args(["hello", "-mt", "1000"])
    assert raw_input.text_input == "hello"
    assert raw_input.max_tokens == 1000

    raw_input, config_path = parse_args(
        [
            "hello",
            "--model",
            "anthropic:claude-3-7-sonnet-20250219",
        ]
    )

    # Not resolved yet
    assert raw_input.provider_name == ""

    # Raw model string
    assert raw_input.model_name == "anthropic:claude-3-7-sonnet-20250219"

    raw_input, config_path = parse_args(
        ["hello", "--prompt-name", "poetry", "--stream"]
    )
    assert raw_input.prompt_name == "poetry"
    assert raw_input.stream is True

    raw_input, config_path = parse_args(["hello", "--config", "/path/to/config"])
    assert config_path == "/path/to/config"
