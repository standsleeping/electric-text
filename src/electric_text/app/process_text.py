# import json
from pathlib import Path
from typing import Literal, Optional

from electric_text.logging import get_logger
# from electric_text.prompts.prose_to_schema.schema_response import SchemaResponse
from electric_text.clients import (
    Client,
    PromptResult,
    # ParseResult,
    build_simple_prompt,
    convert_to_llm_messages,
)

OutputFormat = Literal["text", "json"]

logger = get_logger(__name__)

async def process_text(*, text_input: str, model: str, api_key: Optional[str] = None) -> str:
    """Process the text input.

    Args:
        text_input: The text to be processed
        model: The model to use for generating responses
        api_key: Optional API key for providers that require authentication

    Returns:
        The processed text
    """
    logger.debug(f"Processing {text_input} with model {model}")

    sys_msg_path = Path("src/electric_text/prompts/poetry/poetry.txt")

    sys_msg_content = sys_msg_path.read_text()

    user_prompt = build_simple_prompt(
        sys_msg_content,
        text_input,
    )

    # Split provider:model_name into model_name and provider (only split on first colon)
    provider, model_name = model.split(":", 1)

    logger.debug(f"Model name: {model_name}")
    logger.debug(f"Provider: {provider}")
    logger.debug(f"User prompt: {user_prompt}")

    # Configure client with API key if provided
    config = {}
    if api_key and provider in ["anthropic", "openai"]:
        config["api_key"] = api_key

    client = Client(
        provider_name=provider,
        config=config,
    )

    # client.provider.register_schema(
    #     SchemaResponse,
    #     SchemaResponse.model_json_schema(),
    # )

    llm_messages = convert_to_llm_messages(user_prompt)

    result: PromptResult # ParseResult[SchemaResponse]

    result = await client.generate(
        model=model_name,
        messages=llm_messages,
        # response_model=SchemaResponse,
    )

    # if result.model:
    #     print(f"Result: {result.model}")
    #     print(result.model.model_dump_json(indent=2))

    print(f"Raw content: {result.raw_content}")

    # Step 4: Stream the schema
    async for chunk in client.stream(
        model=model_name,
        messages=llm_messages,
        # response_model=SchemaResponse,
    ):
        # if chunk.model:
        #     print(f"Valid chunk: {chunk.model}")
        #     print(chunk.model.model_dump_json(indent=2))
        
        print(f"Raw chunk content: {chunk.raw_content}")

    full_content = client.provider.stream_history.get_full_content()

    print(f"Full content: {full_content}")

    # try:
    #     print(f"JSON: {json.loads(full_content)}")
    # except json.JSONDecodeError as e:
    #     print(f"Error parsing JSON: {e}")
    #     print(f"Full content: {full_content}")

    return str(full_content)
