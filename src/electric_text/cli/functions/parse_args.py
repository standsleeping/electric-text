import argparse

from typing import List, Optional

from electric_text.shorthand import build_user_shorthand_models
from electric_text.prompting.data.system_input import SystemInput
from electric_text.cli.functions.parse_provider_model import parse_provider_model
from electric_text.configuration import load_config, get_config_value

DEFAULT_MODEL = "ollama:llama3.1:8b"
DEFAULT_LOG_LEVEL = "ERROR"


def parse_args(args: Optional[List[str]] = None) -> SystemInput:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        SystemInput instance with parsed arguments
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
        "openai:gpt-4o-2024-08-06",
    ]

    # Remove duplicates while preserving order
    choices = list(dict.fromkeys(choices))

    # Check for default model in config
    default_model = get_config_value(
        "provider_defaults.default_model",
        DEFAULT_MODEL,
    )

    parser.add_argument(
        "--model",
        "-m",
        choices=choices,
        default=default_model,
        help=f"Model to use for processing (default: {default_model})",
    )

    # Get default log level from config
    default_log_level = get_config_value(
        "logging.level",
        DEFAULT_LOG_LEVEL,
    )

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

    # Load configuration if specified
    if parsed_args.config:
        load_config(parsed_args.config)

    # Split model string into provider_name and model_name
    provider_name, model_name = parse_provider_model(parsed_args.model)

    # Get max_tokens from config if not provided
    max_tokens = parsed_args.max_tokens
    if max_tokens is None:
        max_tokens = None

    return SystemInput(
        text_input=parsed_args.text_input,
        provider_name=provider_name,
        model_name=model_name,
        log_level=parsed_args.log_level,
        api_key=parsed_args.api_key,
        max_tokens=max_tokens,
        prompt_name=parsed_args.prompt_name,
        stream=parsed_args.stream,
        tool_boxes=parsed_args.tool_boxes,
    )
