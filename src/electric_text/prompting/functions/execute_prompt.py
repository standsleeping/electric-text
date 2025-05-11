from typing import Any, List, Optional, Type, Tuple

from electric_text.logging import get_logger
from electric_text.prompting.functions.get_prompt_by_name import get_prompt_by_name
from electric_text.prompting.functions.create_client_request import create_client_request
from electric_text.prompting.functions.execute_client_request import execute_client_request
from electric_text.clients import Client

logger = get_logger(__name__)


async def get_prompt_config_and_model(
    prompt_name: str,
) -> Tuple[Any, Optional[Type[Any]]]:
    """Get prompt config and model class if available.

    Args:
        prompt_name: Name of the prompt to use

    Returns:
        Tuple of (prompt_config, model_class) where model_class may be None
    """
    prompt_config = get_prompt_by_name(prompt_name)
    if not prompt_config:
        logger.error(f"{prompt_name} prompt config not found")
        return None, None

    # Try to get the model class, but it's okay if there isn't one
    model_result = prompt_config.get_model_class()
    if model_result.is_valid and model_result.model_class:
        return prompt_config, model_result.model_class

    # Return the prompt config without a model class if no valid model
    return prompt_config, None


async def execute_prompt(
    *,
    provider_name: str,
    model_name: str,
    text_input: str,
    client: Client,
    tools: Optional[List[Any]] = None,
    prompt_name: Optional[str] = None,
    stream: bool = False,
    max_tokens: Optional[int] = None,
) -> None:
    """Execute a prompt with the given parameters.

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
    """
    # If no prompt_name, handle as a simple request with default system message
    if not prompt_name:
        request = create_client_request(
            provider_name=provider_name,
            model_name=model_name,
            text_input=text_input,
            tools=tools,
            max_tokens=max_tokens,
        )
        
        await execute_client_request(
            client=client,
            request=request,
            stream=stream,
        )
        
        return

    # Get prompt config and model if needed for structured prompts
    config_result = await get_prompt_config_and_model(prompt_name)
    if not config_result[0]:
        return

    prompt_config, model_class = config_result

    # Create request with custom system message from prompt config
    request = create_client_request(
        provider_name=provider_name,
        model_name=model_name,
        text_input=text_input,
        system_message=prompt_config.get_system_message(),
        tools=tools,
        max_tokens=max_tokens,
        response_model=model_class,
    )
    
    # Execute the request with the appropriate model class
    await execute_client_request(
        client=client,
        request=request,
        stream=stream,
        model_class=model_class,
    )