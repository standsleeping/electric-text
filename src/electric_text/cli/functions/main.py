import json
import logging
import traceback
from typing import List, Optional

from electric_text.prompting import generate
from electric_text.logging import configure_logging, get_logger
from electric_text.cli.functions.parse_args import parse_args
from electric_text.prompting.data.system_input import SystemInput
from electric_text.prompting.functions.output_conversion.system_output_to_dict import (
    system_output_to_dict,
)


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

        if system_input.stream:
            stream_result = await generate(
                text_input=system_input.text_input,
                provider_name=system_input.provider_name,
                model_name=system_input.model_name,
                log_level=system_input.log_level,
                api_key=system_input.api_key,
                max_tokens=system_input.max_tokens,
                prompt_name=system_input.prompt_name,
                stream=True,
                tool_boxes=system_input.tool_boxes,
            )

            async for output in stream_result:
                output_dict = system_output_to_dict(output)
                print(json.dumps(output_dict))

        else:
            result = await generate(
                text_input=system_input.text_input,
                provider_name=system_input.provider_name,
                model_name=system_input.model_name,
                log_level=system_input.log_level,
                api_key=system_input.api_key,
                max_tokens=system_input.max_tokens,
                prompt_name=system_input.prompt_name,
                stream=False,
                tool_boxes=system_input.tool_boxes,
            )

            output_dict = system_output_to_dict(result)
            print(json.dumps(output_dict))

        return 0
    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Error during execution: {e}")
        return 1
