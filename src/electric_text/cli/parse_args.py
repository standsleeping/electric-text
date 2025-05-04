import argparse

from typing import List, Optional

from electric_text.shorthand.build_user_shorthand_models import (
    build_user_shorthand_models,
)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="electric_text",
        description="This text is electric!",
    )

    parser.add_argument(
        "text_input",
        type=str,
        help="Text to be processed",
    )

    models = build_user_shorthand_models()

    shorthands = list(models.keys())

    choices = shorthands + [
        "ollama:llama3.1:8b",
        "anthropic:claude-3-7-sonnet-20250219",
        "openai:gpt-4o-mini",
    ]

    parser.add_argument(
        "--model",
        "-m",
        choices=choices,
        default="ollama:llama3.1:8b",
        help="Model to use for processing (default: llama3.1:8b)",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="ERROR",
        help="Set the logging level (default: INFO)",
    )

    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="API key for providers that require authentication (e.g., Anthropic)",
    )

    parser.add_argument(
        "--max-tokens",
        "-mt",
        type=int,
        help="Maximum number of tokens to generate",
    )

    return parser.parse_args(args)
