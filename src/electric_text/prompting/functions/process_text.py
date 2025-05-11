from typing import Optional, Any, List

from electric_text.logging import get_logger
from electric_text.clients import create_user_request
from electric_text.clients import resolve_api_key
from electric_text.clients import Client
from electric_text.clients import ProviderResponse
from electric_text.tools import load_tools_from_tool_boxes
from electric_text.prompting.functions.execute_prompt import execute_prompt

logger = get_logger(__name__)


async def process_text(
    *,
    text_input: str,
    provider_name: str,
    model_name: str,
    api_key: Optional[str] = None,
    max_tokens: Optional[int] = None,
    prompt_name: Optional[str] = None,
    stream: bool = False,
    tool_boxes: Optional[str] = None,
) -> None:
    """Process the text input.

    Args:
        text_input: The text to be processed
        provider_name: The provider to use
        model_name: The model to use in format "provider:model_name"
        api_key: Optional API key for providers that require authentication
        max_tokens: Maximum number of tokens to generate
        prompt_name: Optional name of the prompt to use
        stream: Whether to stream the response
        tool_boxes: Optional comma-separated list of tool box names to use

    Returns:
        The processed text
    """
    logger.debug(f"Processing {text_input}")
    logger.debug(f"Model name: {model_name}")
    logger.debug(f"Provider: {provider_name}")

    # Configure client with API key if available
    config = {}
    resolved_api_key = resolve_api_key(provider_name, api_key)
    if resolved_api_key:
        config["api_key"] = resolved_api_key

    client = Client(
        provider_name=provider_name,
        config=config,
    )

    # Parse tool_boxes string into a list if provided
    tool_box_list: List[str] = []
    if tool_boxes:
        tool_box_list = [tb.strip() for tb in tool_boxes.split(",")]
        logger.debug(f"Using tool boxes: {tool_box_list}")

        # Load and process tools from the specified tool boxes
        tools = load_tools_from_tool_boxes(tool_box_list)
        logger.debug(f"Loaded {len(tools)} tools from {len(tool_box_list)} tool boxes")
    else:
        tools = []

    if prompt_name:
        # Use the execute_prompt function with the provided parameters
        await execute_prompt(
            model_name=model_name,
            provider_name=provider_name,
            text_input=text_input,
            client=client,
            prompt_name=prompt_name,
            stream=stream,
            tool_boxes=tool_box_list,
        )
    else:
        # Use the original simple approach with no specific prompt
        request = create_user_request(
            model_name=model_name,
            provider_name=provider_name,
            text_input=text_input,
            max_tokens=max_tokens,
            tool_boxes=tool_box_list,
            tools=tools,
        )

        result: ProviderResponse[Any] = await client.generate(
            request=request,
        )

        print(result.raw_content)
