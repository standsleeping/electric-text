import os
from typing import List

from electric_text.logging import get_logger
from electric_text.clients import resolve_api_key
from electric_text.clients import Client
from electric_text.tools import load_tools_from_tool_boxes
from electric_text.prompting.functions.execute_prompt import execute_prompt
from electric_text.prompting.data.system_input import SystemInput
from electric_text.prompting.functions.get_http_logging_enabled import get_http_logging_enabled
from electric_text.prompting.functions.get_http_log_dir import get_http_log_dir

logger = get_logger(__name__)


async def process_text(system_input: SystemInput) -> None:
    """Process the text input.

    Args:
        system_input: SystemInput containing parameters for text processing

    Returns:
        None (prints the result)
    """
    logger.debug(f"Processing {system_input.text_input}")
    logger.debug(f"Model name: {system_input.model_name}")
    logger.debug(f"Provider: {system_input.provider_name}")

    # Configure client with API key if available
    config = {}
    resolved_api_key = resolve_api_key(system_input.provider_name, system_input.api_key)
    if resolved_api_key:
        config["api_key"] = resolved_api_key

    # Resolve HTTP logging configuration
    http_logging_enabled = get_http_logging_enabled()
    http_log_dir = get_http_log_dir()
    
    client = Client(
        provider_name=system_input.provider_name,
        config=config,
        http_logging_enabled=http_logging_enabled,
        http_log_dir=http_log_dir,
    )

    # Parse tool_boxes string into a list if provided
    tool_box_list: List[str] = []
    tools = []
    if system_input.tool_boxes:
        tool_box_list = [tb.strip() for tb in system_input.tool_boxes.split(",")]
        logger.debug(f"Using tool boxes: {tool_box_list}")

        # Load and process tools from the specified tool boxes
        tools = load_tools_from_tool_boxes(tool_box_list)
        logger.debug(f"Loaded {len(tools)} tools from {len(tool_box_list)} tool boxes")

    # Execute the prompt
    await execute_prompt(
        client=client,
        tools=tools,
        model_name=system_input.model_name,
        provider_name=system_input.provider_name,
        text_input=system_input.text_input,
        prompt_name=system_input.prompt_name,
        stream=system_input.stream,
        max_tokens=system_input.max_tokens,
    )
