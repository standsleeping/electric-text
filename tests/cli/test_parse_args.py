"""Tests for the command-line interface."""

from electric_text.cli import parse_args


def test_parse_args() -> None:
    """Test argument parsing."""
    args = parse_args(["hello"])
    assert args.text_input == "hello"
    assert args.format == "text"
    assert args.log_level == "INFO"

    args = parse_args(["hello", "--format", "json"])
    assert args.text_input == "hello"
    assert args.format == "json"
    assert args.log_level == "INFO"

    args = parse_args(["hello", "-f", "json", "--log-level", "DEBUG"])
    assert args.text_input == "hello"
    assert args.format == "json"
    assert args.log_level == "DEBUG"
