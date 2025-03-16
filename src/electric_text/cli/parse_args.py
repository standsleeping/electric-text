import argparse

from typing import List, Optional


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

    parser.add_argument(
        "--model",
        "-m",
        choices=["ollama:llama3.1:8b"],
        default="ollama:llama3.1:8b",
        help="Model to use for processing (default: llama3.1:8b)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    return parser.parse_args(args)
