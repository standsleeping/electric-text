import json
from pathlib import Path
from typing import Literal, Optional, Union, AsyncGenerator, Any

from electric_text.logging import get_logger
from electric_text.prompts.prose_to_schema.schema_response import SchemaResponse
from electric_text.clients.data.user_request import UserRequest
from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients.functions.split_model_string import split_model_string
from electric_text.clients import (
    Client,
    PromptResult,
    ParseResult,
)
from electric_text.clients.data.provider_response import ProviderResponse

OutputFormat = Literal["text", "json"]

logger = get_logger(__name__)


async def process_text(
    *, text_input: str, model: str, api_key: Optional[str] = None
) -> str:
    """Process the text input.

    Args:
        text_input: The text to be processed
        model: The model to use in format "provider:model_name"
        api_key: Optional API key for providers that require authentication

    Returns:
        The processed text
    """
    logger.debug(f"Processing {text_input} with model {model}")

    # Split the model string to get provider and model name
    provider_name, model_name = split_model_string(model)

    # Read system message files
    sys_msg_path = Path("src/electric_text/prompts/prose_to_schema/prose-to-schema.txt")
    poetry_system_msg = Path("src/electric_text/prompts/poetry/poetry.txt")

    structured_sys_msg = sys_msg_path.read_text()
    poetry_sys_msg = poetry_system_msg.read_text()

    # Configure client with API key if provided
    config = {}
    if api_key and provider_name in ["anthropic", "openai"]:
        config["api_key"] = api_key

    client = Client(
        provider_name=provider_name,
        config=config,
    )

    logger.debug(f"Model name: {model_name}")
    logger.debug(f"Provider: {provider_name}")

    # Create a UserRequest for unstructured poetry generation
    poetry_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=poetry_sys_msg,
        text_input=text_input,
    )

    # Generate unstructured poetry response
    unstructured_result: ProviderResponse[None] = await client.generate(
        request=poetry_request,
    )

    # Direct access to raw content regardless of result type
    print(f"Raw content: {unstructured_result.raw_content}")

    # Create a UserRequest for structured schema generation
    schema_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=structured_sys_msg,
        text_input=text_input,
        response_model=SchemaResponse,
    )

    # Generate structured schema response with type annotation
    structured_result: ProviderResponse[SchemaResponse] = await client.generate(
        request=schema_request,
    )

    # Unified interface for accessing parsed model and checking validity
    if structured_result.is_valid and structured_result.parsed_model:
        print(f"Result: {structured_result.parsed_model}")
        print(structured_result.parsed_model.model_dump_json(indent=2))

    print(f"Unstructured raw content: {unstructured_result.raw_content}")

    # Stream unstructured poetry content
    poetry_stream_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=poetry_sys_msg,
        text_input=text_input,
        stream=True,
    )

    poetry_stream_generator: AsyncGenerator[ProviderResponse[Any], None] = (
        client.stream(
            request=poetry_stream_request,
        )
    )

    # All chunks use the same ProviderResponse interface
    async for chunk in poetry_stream_generator:
        print(f"Raw chunk content: {chunk.raw_content}")

    full_content = client.provider.stream_history.get_full_content()
    print(f"Full content: {full_content}")

    # Create a UserRequest for structured schema streaming
    schema_stream_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=structured_sys_msg,
        text_input=text_input,
        response_model=SchemaResponse,
        stream=True,
    )

    # Stream the structured schema with consistent typing
    schema_stream_generator: AsyncGenerator[ProviderResponse[SchemaResponse], None] = (
        client.stream(
            request=schema_stream_request,
        )
    )

    # Unified interface for all chunks
    async for structured_chunk in schema_stream_generator:
        if structured_chunk.is_valid and structured_chunk.parsed_model:
            print(f"Valid chunk: {structured_chunk.parsed_model}")
            print(structured_chunk.parsed_model.model_dump_json(indent=2))

        # All chunks have raw_content
        print(f"Raw chunk content: {structured_chunk.raw_content}")

    structured_full_content = client.provider.stream_history.get_full_content()
    print(f"Structured full content: {structured_full_content}")

    try:
        print(f"JSON: {json.loads(structured_full_content)}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Structured full content: {structured_full_content}")

    return str(full_content)
