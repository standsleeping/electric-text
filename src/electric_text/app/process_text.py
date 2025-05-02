import json
from pathlib import Path
from typing import Literal, Optional, AsyncGenerator, Any

from electric_text.logging import get_logger
from electric_text.prompts.prose_to_schema.schema_response import SchemaResponse
from electric_text.clients.data.user_request import UserRequest
from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients.functions.split_model_string import split_model_string
from electric_text.clients import Client
from electric_text.clients.data.provider_response import ProviderResponse

OutputFormat = Literal["text", "json"]

logger = get_logger(__name__)


def temp_example_sys_msgs() -> tuple[str, str]:
    # Read system message files
    sys_msg_path = Path("src/electric_text/prompts/prose_to_schema/prose-to-schema.txt")
    poetry_system_msg = Path("src/electric_text/prompts/poetry/poetry.txt")

    structured_sys_msg = sys_msg_path.read_text()
    poetry_sys_msg = poetry_system_msg.read_text()

    return structured_sys_msg, poetry_sys_msg


async def temp_example_structured_request(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    structured_sys_msg, _ = temp_example_sys_msgs()

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


async def temp_example_poetry_request(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    _, poetry_sys_msg = temp_example_sys_msgs()

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


async def temp_example_poetry_stream(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    _, poetry_sys_msg = temp_example_sys_msgs()

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


async def temp_example_structured_stream(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    structured_sys_msg, _ = temp_example_sys_msgs()

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


async def process_text(
    *,
    text_input: str,
    model: str,
    api_key: Optional[str] = None,
) -> None:
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

    request = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        text_input=text_input,
    )

    result: ProviderResponse[Any] = await client.generate(
        request=request,
    )

    print(result.raw_content)