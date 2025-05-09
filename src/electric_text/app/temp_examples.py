import json
from typing import AsyncGenerator, Any

from electric_text.logging import get_logger
from electric_text.clients.data.user_request import UserRequest
from electric_text.clients.functions.create_user_request import create_user_request
from electric_text.clients import Client
from electric_text.clients.data.provider_response import ProviderResponse
from .get_prompt_by_name import get_prompt_by_name

logger = get_logger(__name__)


async def temp_example_structured_request(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    # Get prompt config for structured schema generation
    prompt_config = get_prompt_by_name("prose_to_schema")
    if not prompt_config:
        logger.error("Prose to schema prompt config not found")
        return

    # Get the system message and response model
    system_message = prompt_config.get_system_message()
    model_result = prompt_config.get_model_class()
    if not model_result.is_valid or not model_result.model_class:
        logger.error(f"Failed to load schema model: {model_result.error_message}")
        return

    schema_response_model = model_result.model_class

    # Create a UserRequest for structured schema generation
    schema_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=system_message,
        text_input=text_input,
        response_model=schema_response_model,
    )

    # Generate structured schema response with type annotation
    structured_result: ProviderResponse[Any] = await client.generate(
        request=schema_request,
    )

    # Unified interface for accessing parsed model and checking validity
    if structured_result.is_valid and structured_result.parsed_model:
        print(f"Result: {structured_result.parsed_model}")
        print(structured_result.parsed_model.model_dump_json(indent=2))


async def temp_example_structured_stream(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    # Get prompt config for structured schema generation
    prompt_config = get_prompt_by_name("prose_to_schema")
    if not prompt_config:
        logger.error("Prose to schema prompt config not found")
        return

    # Get the system message and response model
    system_message = prompt_config.get_system_message()
    model_result = prompt_config.get_model_class()
    if not model_result.is_valid or not model_result.model_class:
        logger.error(f"Failed to load schema model: {model_result.error_message}")
        return

    schema_response_model = model_result.model_class

    # Create a UserRequest for structured schema streaming
    schema_stream_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=system_message,
        text_input=text_input,
        response_model=schema_response_model,
        stream=True,
    )

    # Stream the structured schema with consistent typing
    schema_stream_generator: AsyncGenerator[ProviderResponse[Any], None] = (
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


async def temp_example_poetry_request(
    model_name: str,
    provider_name: str,
    text_input: str,
    client: Client,
) -> None:
    # Get prompt config for poetry generation
    prompt_config = get_prompt_by_name("poetry")
    if not prompt_config:
        logger.error("Poetry prompt config not found")
        return

    # Get the system message
    system_message = prompt_config.get_system_message()

    # Create a UserRequest for unstructured poetry generation
    poetry_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=system_message,
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
    # Get prompt config for poetry generation
    prompt_config = get_prompt_by_name("poetry")
    if not prompt_config:
        logger.error("Poetry prompt config not found")
        return

    # Get the system message
    system_message = prompt_config.get_system_message()

    # Stream unstructured poetry content
    poetry_stream_request: UserRequest = create_user_request(
        model_name=model_name,
        provider_name=provider_name,
        system_message=system_message,
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
