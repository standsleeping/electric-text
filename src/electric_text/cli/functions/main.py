import logging
import traceback
from typing import List, Optional

from electric_text.prompting import process_text
from electric_text.logging import configure_logging, get_logger
from electric_text.cli.functions.parse_args import parse_args
from electric_text.cli.data.system_input import SystemInput


async def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    system_input: SystemInput = parse_args(args)

    log_level = getattr(logging, system_input.log_level)
    configure_logging(level=log_level)
    logger = get_logger(__name__)

    try:
        logger.debug(f"Processing with system input: {system_input}")

        await process_text(system_input)

        return 0
    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Error during execution: {e}")
        return 1
