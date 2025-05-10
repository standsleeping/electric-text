import json
from typing import AsyncGenerator, Any, Optional, Type, TypeVar, Tuple, List

from electric_text.logging import get_logger
from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients import Client
from electric_text.clients.data.provider_response import ProviderResponse
from electric_text.prompting.functions.get_prompt_by_name import get_prompt_by_name
from electric_text.tools import load_tools_from_tool_boxes

logger = get_logger(__name__)

T = TypeVar("T")


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
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
    prompt_name: str,
    stream: bool = False,
    tool_boxes: Optional[List[str]] = None,
) -> None:
    """Execute a prompt with the given parameters.

    This function handles both structured and unstructured prompts,
    with or without streaming, based on the prompt configuration.

    Args:
        model_name: Name of the model to use
        provider_name: Name of the provider to use
        text_input: Input text to process
        client: Client instance to use for the request
        prompt_name: Name of the prompt to use
        stream: Whether to stream the response
        tool_boxes: Optional list of tool box names to use
    """
    # Get prompt config and model if needed
    config_result = await get_prompt_config_and_model(prompt_name)
    if not config_result[0]:
        return

    prompt_config, model_class = config_result

    # Create request
    request_args = {
        "model_name": model_name,
        "provider_name": provider_name,
        "system_message": prompt_config.get_system_message(),
        "text_input": text_input,
        "stream": stream,
    }

    # Load tools if tool_boxes are provided
    if tool_boxes:
        request_args["tool_boxes"] = tool_boxes
        # Load the tools
        tools = load_tools_from_tool_boxes(tool_boxes)
        request_args["tools"] = tools

    if model_class:
        request_args["response_model"] = model_class

    user_request = create_user_request(**request_args)

    if not stream:
        # Handle non-streaming request
        response_result: ProviderResponse[Any] = await client.generate(
            request=user_request
        )

        if model_class and response_result.is_valid and response_result.parsed_model:
            print(f"Result: {response_result.parsed_model}")
            print(response_result.parsed_model.model_dump_json(indent=2))
        else:
            print(f"Raw content: {response_result.raw_content}")
    else:
        # Handle streaming request
        generator: AsyncGenerator[ProviderResponse[Any], None] = client.stream(
            request=user_request
        )

        async for chunk in generator:
            if model_class and chunk.is_valid and chunk.parsed_model:
                print(f"Valid chunk: {chunk.parsed_model}")
                print(chunk.parsed_model.model_dump_json(indent=2))

            print(f"Raw chunk content: {chunk.raw_content}")

        full_content = client.provider.stream_history.get_full_content()
        print(f"Full content: {full_content}")

        if model_class:
            try:
                print(f"JSON: {json.loads(full_content)}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Structured full content: {full_content}")
