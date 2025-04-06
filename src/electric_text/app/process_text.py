import json
from pathlib import Path
from typing import Literal, Optional

from electric_text.logging import get_logger
from electric_text.prompts.prose_to_schema.schema_response import SchemaResponse
from electric_text.clients import (
    Client,
    PromptResult,
    ParseResult,
    build_simple_prompt,
    convert_to_llm_messages,
)

OutputFormat = Literal["text", "json"]

logger = get_logger(__name__)


async def process_text(
    *, text_input: str, model: str, api_key: Optional[str] = None
) -> str:
    """Process the text input.

    Args:
        text_input: The text to be processed
        model: The model to use for generating responses
        api_key: Optional API key for providers that require authentication

    Returns:
        The processed text
    """
    logger.debug(f"Processing {text_input} with model {model}")

    sys_msg_path = Path("src/electric_text/prompts/prose_to_schema/prose-to-schema.txt")
    poetry_system_msg = Path("src/electric_text/prompts/poetry/poetry.txt")

    sys_msg_content = sys_msg_path.read_text()
    poetry_sys_msg_content = poetry_system_msg.read_text()

    structured_user_prompt = build_simple_prompt(
        sys_msg_content,
        text_input,
    )

    poetry_user_prompt = build_simple_prompt(
        poetry_sys_msg_content,
        text_input,
    )

    # Split provider:model_name into model_name and provider (only split on first colon)
    provider, model_name = model.split(":", 1)

    logger.debug(f"Model name: {model_name}")
    logger.debug(f"Provider: {provider}")
    logger.debug(f"Structured user prompt: {structured_user_prompt}")
    logger.debug(f"Poetry user prompt: {poetry_user_prompt}")

    # Configure client with API key if provided
    config = {}
    if api_key and provider in ["anthropic", "openai"]:
        config["api_key"] = api_key

    client = Client(
        provider_name=provider,
        config=config,
    )

    poetry_llm_messages = convert_to_llm_messages(poetry_user_prompt)
    structured_llm_messages = convert_to_llm_messages(structured_user_prompt)

    unstructured_result: PromptResult

    unstructured_result = await client.generate(
        model=model_name,
        messages=poetry_llm_messages,
    )

    print(f"Raw content: {unstructured_result.raw_content}")

    structured_result: ParseResult[SchemaResponse] = await client.structured_generate(
        model=model_name,
        messages=structured_llm_messages,
        response_model=SchemaResponse,
    )

    if structured_result.model:
        print(f"Result: {structured_result.model}")
        print(structured_result.model.model_dump_json(indent=2))

    print(f"Unstructured raw content: {unstructured_result.raw_content}")

    # Stream content
    async for chunk in client.stream(
        model=model_name,
        messages=poetry_llm_messages,
    ):
        print(f"Raw chunk content: {chunk.raw_content}")

    full_content = client.provider.stream_history.get_full_content()

    print(f"Full content: {full_content}")

    # Stream the schema
    async for structured_chunk in client.structured_stream(
        model=model_name,
        messages=structured_llm_messages,
        response_model=SchemaResponse,
    ):
        if structured_chunk.model:
            print(f"Valid chunk: {structured_chunk.model}")
            print(structured_chunk.model.model_dump_json(indent=2))

        print(f"Raw chunk content: {structured_chunk.raw_content}")

    structured_full_content = client.provider.stream_history.get_full_content()

    print(f"Structured full content: {structured_full_content}")

    try:
        print(f"JSON: {json.loads(structured_full_content)}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Structured full content: {structured_full_content}")

    return str(full_content)
