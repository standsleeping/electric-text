import logging
import traceback
from typing import List, Optional

from electric_text.prompting import process_text
from electric_text.logging import configure_logging, get_logger
from electric_text.cli.parse_args import parse_args
from electric_text.cli.functions.parse_provider_model import parse_provider_model


async def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    parsed_args = parse_args(args)

    log_level = getattr(logging, parsed_args.log_level)
    configure_logging(level=log_level)
    logger = get_logger(__name__)

    try:
        logger.debug(f"Processing arguments: {parsed_args}")

        # Split the model string to get provider and model name
        provider_name, model_name = parse_provider_model(parsed_args.model)

        await process_text(
            text_input=parsed_args.text_input,
            provider_name=provider_name,
            model_name=model_name,
            api_key=parsed_args.api_key,
            max_tokens=parsed_args.max_tokens,
            prompt_name=parsed_args.prompt_name,
            stream=parsed_args.stream,
            tool_boxes=parsed_args.tool_boxes,
        )

        return 0
    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Error during execution: {e}")
        return 1
