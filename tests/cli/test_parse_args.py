"""Tests for the command-line interface."""

from electric_text.cli import parse_args


def test_parse_args() -> None:
    """Test argument parsing."""
    args = parse_args(["hello"])
    assert args.text_input == "hello"
    assert args.log_level == "ERROR"
    assert args.max_tokens is None

    args = parse_args(["hello", "--log-level", "DEBUG"])
    assert args.text_input == "hello"
    assert args.log_level == "DEBUG"
    assert args.max_tokens is None

    args = parse_args(["hello", "--max-tokens", "500"])
    assert args.text_input == "hello"
    assert args.max_tokens == 500

    args = parse_args(["hello", "-mt", "1000"])
    assert args.text_input == "hello"
    assert args.max_tokens == 1000
