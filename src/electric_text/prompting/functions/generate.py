from typing import List, Union, AsyncGenerator, overload, Literal

from electric_text.logging import get_logger
from electric_text.clients import resolve_api_key
from electric_text.clients import Client
from electric_text.tools import load_tools_from_tool_boxes
from electric_text.prompting.data.system_input import SystemInput
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.functions.execute_prompt_with_return import (
    execute_prompt_with_return,
)
from electric_text.prompting.functions.get_http_logging_enabled import get_http_logging_enabled
from electric_text.prompting.functions.get_http_log_dir import get_http_log_dir

logger = get_logger(__name__)


@overload
async def generate(
    text_input: str,
    provider_name: str,
    model_name: str,
    log_level: str = "ERROR",
    api_key: str | None = None,
    max_tokens: int | None = None,
    prompt_name: str | None = None,
    *,
    stream: Literal[False] = False,
    tool_boxes: str | None = None,
) -> SystemOutput: ...


@overload
async def generate(
    text_input: str,
    provider_name: str,
    model_name: str,
    log_level: str = "ERROR",
    api_key: str | None = None,
    max_tokens: int | None = None,
    prompt_name: str | None = None,
    *,
    stream: Literal[True],
    tool_boxes: str | None = None,
) -> AsyncGenerator[SystemOutput, None]: ...


async def generate(
    text_input: str,
    provider_name: str,
    model_name: str,
    log_level: str = "ERROR",
    api_key: str | None = None,
    max_tokens: int | None = None,
    prompt_name: str | None = None,
    stream: bool = False,
    tool_boxes: str | None = None,
) -> Union[SystemOutput, AsyncGenerator[SystemOutput, None]]:
    """Generate text using the electric_text system.

    This function provides a notebook-friendly interface to the electric_text
    system, returning the result as a SystemOutput object or an async generator
    of SystemOutput objects when streaming.

    Args:
        text_input: The text to be processed
        provider_name: The provider to use (e.g., "anthropic", "openai", "ollama")
        model_name: The model to use (e.g., "claude-3-7-sonnet-20250219")
        log_level: Logging level to use (default: "ERROR")
        api_key: Optional API key for providers that require authentication
        max_tokens: Maximum number of tokens to generate
        prompt_name: Optional name of the prompt to use
        stream: Whether to stream the response (default: False)
        tool_boxes: Optional comma-separated list of tool box names to use

    Returns:
        SystemOutput: The processed result (when stream=False)
        AsyncGenerator[SystemOutput, None]: Stream of results (when stream=True)
    """
    # Create SystemInput from individual parameters
    system_input = SystemInput(
        text_input=text_input,
        provider_name=provider_name,
        model_name=model_name,
        log_level=log_level,
        api_key=api_key,
        max_tokens=max_tokens,
        prompt_name=prompt_name,
        stream=stream,
        tool_boxes=tool_boxes,
    )

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

    # Execute the prompt and return the result
    return await execute_prompt_with_return(
        client=client,
        tools=tools,
        model_name=system_input.model_name,
        provider_name=system_input.provider_name,
        text_input=system_input.text_input,
        prompt_name=system_input.prompt_name,
        stream=system_input.stream,
        max_tokens=system_input.max_tokens,
    )
