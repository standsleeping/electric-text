import logging
import traceback
from typing import List, Optional

from electric_text.app import process_text
from electric_text.logging import configure_logging, get_logger

from .parse_args import parse_args


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

        await process_text(
            text_input=parsed_args.text_input,
            model=parsed_args.model,
            api_key=parsed_args.api_key,
            max_tokens=parsed_args.max_tokens,
            prompt_name=parsed_args.prompt_name,
            stream=parsed_args.stream,
        )

        return 0
    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Error during execution: {e}")
        return 1
