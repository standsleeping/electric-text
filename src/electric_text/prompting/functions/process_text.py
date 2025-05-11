from typing import Any, List

from electric_text.logging import get_logger
from electric_text.clients import create_user_request
from electric_text.clients import resolve_api_key
from electric_text.clients import Client
from electric_text.clients import ProviderResponse
from electric_text.tools import load_tools_from_tool_boxes
from electric_text.prompting.functions.execute_prompt import execute_prompt
from electric_text.cli.data.system_input import SystemInput

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

    client = Client(
        provider_name=system_input.provider_name,
        config=config,
    )

    # Parse tool_boxes string into a list if provided
    tool_box_list: List[str] = []
    if system_input.tool_boxes:
        tool_box_list = [tb.strip() for tb in system_input.tool_boxes.split(",")]
        logger.debug(f"Using tool boxes: {tool_box_list}")

        # Load and process tools from the specified tool boxes
        tools = load_tools_from_tool_boxes(tool_box_list)
        logger.debug(f"Loaded {len(tools)} tools from {len(tool_box_list)} tool boxes")
    else:
        tools = []

    if system_input.prompt_name:
        # Use the execute_prompt function with the provided parameters
        await execute_prompt(
            model_name=system_input.model_name,
            provider_name=system_input.provider_name,
            text_input=system_input.text_input,
            client=client,
            prompt_name=system_input.prompt_name,
            stream=system_input.stream,
            tool_boxes=tool_box_list,
        )
    else:
        # Use the original simple approach with no specific prompt
        request = create_user_request(
            model_name=system_input.model_name,
            provider_name=system_input.provider_name,
            text_input=system_input.text_input,
            max_tokens=system_input.max_tokens,
            tool_boxes=tool_box_list,
            tools=tools,
        )

        result: ProviderResponse[Any] = await client.generate(
            request=request,
        )

        print(result.raw_content)
