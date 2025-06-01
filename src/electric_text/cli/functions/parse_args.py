import argparse
from typing import List, Optional

from electric_text.prompting.data.system_input import SystemInput
from electric_text.prompting.functions.get_model_choices import get_model_choices
from electric_text.prompting.functions.get_default_model import get_default_model
from electric_text.prompting.functions.get_default_log_level import (
    get_default_log_level,
)

DEFAULT_MODEL = "ollama:llama3.1:8b"
DEFAULT_LOG_LEVEL = "ERROR"


def parse_args(args: Optional[List[str]] = None) -> tuple[SystemInput, Optional[str]]:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Tuple of (SystemInput with raw parsed arguments, config_path if specified)
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

    # Get model choices and default from prompting layer
    choices = get_model_choices()
    default_model = get_default_model()

    parser.add_argument(
        "--model",
        "-m",
        choices=choices,
        default=default_model,
        help=f"Model to use for processing (default: {default_model})",
    )

    # Get default log level from prompting layer
    default_log_level = get_default_log_level()

    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=default_log_level,
        help=f"Set the logging level (default: {default_log_level})",
    )

    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        help="API key for providers that require authentication (e.g., Anthropic)",
    )

    # Get default max tokens from config based on the model
    parser.add_argument(
        "--max-tokens",
        "-mt",
        type=int,
        help="Maximum number of tokens to generate",
    )

    parser.add_argument(
        "--prompt-name",
        "-p",
        type=str,
        choices=["prose_to_schema", "structured_poem", "poetry"],
        help="Name of the prompt to use (if not specified, uses default system message)",
    )

    parser.add_argument(
        "--stream",
        "-st",
        action="store_true",
        help="Stream the response",
    )

    parser.add_argument(
        "--tool-boxes",
        "-tb",
        type=str,
        help="List of tool boxes to use (comma-separated, e.g., 'meteorology,travel')",
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file",
    )

    parsed_args = parser.parse_args(args)

    # Return raw SystemInput - configuration resolution happens in prompting layer
    return SystemInput(
        text_input=parsed_args.text_input,
        provider_name="",  # Will be resolved from model string in prompting layer
        model_name=parsed_args.model,  # Raw model string (may be shorthand)
        log_level=parsed_args.log_level,
        api_key=parsed_args.api_key,
        max_tokens=parsed_args.max_tokens,
        prompt_name=parsed_args.prompt_name,
        stream=parsed_args.stream,
        tool_boxes=parsed_args.tool_boxes,
    ), parsed_args.config
