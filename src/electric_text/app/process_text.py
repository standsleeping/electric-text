from typing import Optional, Any

from electric_text.logging import get_logger
from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients.functions.parse_provider_model import parse_provider_model
from electric_text.clients.functions.resolve_api_key import resolve_api_key
from electric_text.clients import Client
from electric_text.clients.data.provider_response import ProviderResponse


from electric_text.app.temp_examples import (
    temp_example_structured_request,
    temp_example_structured_stream,
    temp_example_poetry_request,
    temp_example_poetry_stream,
)

logger = get_logger(__name__)


async def process_text(
    *,
    text_input: str,
    model: str,
    api_key: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> None:
    """Process the text input.

    Args:
        text_input: The text to be processed
        model: The model to use in format "provider:model_name"
        api_key: Optional API key for providers that require authentication
        max_tokens: Maximum number of tokens to generate

    Returns:
        The processed text
    """
    logger.debug(f"Processing {text_input} with model {model}")

    # Split the model string to get provider and model name
    provider_name, model_name = parse_provider_model(model)

    # Configure client with API key if available
    config = {}
    resolved_api_key = resolve_api_key(provider_name, api_key)
    if resolved_api_key:
        config["api_key"] = resolved_api_key

    client = Client(
        provider_name=provider_name,
        config=config,
    )

    logger.debug(f"Model name: {model_name}")
    logger.debug(f"Provider: {provider_name}")

    request = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        text_input=text_input,
        max_tokens=max_tokens,
    )

    result: ProviderResponse[Any] = await client.generate(
        request=request,
    )

    print(result.raw_content)

    # await temp_example_structured_request(
    #     model_name=model_name,
    #     provider_name=provider_name,
    #     text_input=text_input,
    #     client=client,
    # )

    # await temp_example_structured_stream(
    #     model_name=model_name,
    #     provider_name=provider_name,
    #     text_input=text_input,
    #     client=client,
    # )

    # await temp_example_poetry_request(
    #     model_name=model_name,
    #     provider_name=provider_name,
    #     text_input=text_input,
    #     client=client,
    # )

    # await temp_example_poetry_stream(
    #     model_name=model_name,
    #     provider_name=provider_name,
    #     text_input=text_input,
    #     client=client,
    # )
