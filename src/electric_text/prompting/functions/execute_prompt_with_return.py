from typing import Any, List, Optional, Union, AsyncGenerator

from electric_text.logging import get_logger
from electric_text.clients import Client
from electric_text.clients.data.default_output_schema import DefaultOutputSchema
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.functions.create_client_request import (
    create_client_request,
)
from electric_text.prompting.functions.execute_client_request_with_return import (
    execute_client_request_with_return,
)
from electric_text.prompting.functions.get_prompt_config_and_model import (
    get_prompt_config_and_model,
)


logger = get_logger(__name__)


async def execute_prompt_with_return(
    *,
    provider_name: str,
    model_name: str,
    text_input: str,
    client: Client,
    tools: Optional[List[Any]] = None,
    prompt_name: Optional[str] = None,
    stream: bool = False,
    max_tokens: Optional[int] = None,
) -> Union[SystemOutput, AsyncGenerator[SystemOutput, None]]:
    """Execute a prompt with the given parameters and return the result.

    This function handles both structured and unstructured prompts,
    with or without streaming, based on the prompt configuration.
    If no prompt_name is provided, it will create a simple user request.

    Args:
        model_name: Name of the model to use
        provider_name: Name of the provider to use
        text_input: Input text to process
        client: Client instance to use for the request
        prompt_name: Optional name of the prompt to use
        stream: Whether to stream the response
        tool_boxes: Optional list of tool box names to use
        max_tokens: Optional maximum number of tokens for completion
        tools: Optional list of pre-loaded tools

    Returns:
        SystemOutput if stream=False, AsyncGenerator[SystemOutput, None] if stream=True
    """
    # If no prompt_name, handle as a simple request with default system message
    if not prompt_name:
        no_prompt_request = create_client_request(
            provider_name=provider_name,
            model_name=model_name,
            text_input=text_input,
            tools=tools,
            max_tokens=max_tokens,
            output_schema=DefaultOutputSchema,
        )

        return await execute_client_request_with_return(
            client=client,
            request=no_prompt_request,
            stream=stream,
        )

    # Get prompt config and model if needed for structured prompts
    prompt_config, model_class = await get_prompt_config_and_model(prompt_name)

    if not prompt_config:
        logger.error(f"{prompt_name} prompt config not found")
        raise ValueError(f"Prompt config '{prompt_name}' not found")

    # Create request with custom system message from prompt config
    request = create_client_request(
        provider_name=provider_name,
        model_name=model_name,
        text_input=text_input,
        system_message=prompt_config.get_system_message(),
        tools=tools,
        max_tokens=max_tokens,
        output_schema=model_class,
    )

    # Execute the request with the appropriate model class
    return await execute_client_request_with_return(
        client=client,
        request=request,
        stream=stream,
    )
