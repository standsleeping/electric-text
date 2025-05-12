import json
from typing import Any, AsyncGenerator, Optional, Type

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.logging import get_logger

logger = get_logger(__name__)


async def execute_client_request(
    *,
    client: Client,
    request: ClientRequest,
    stream: bool = False,
    model_class: Optional[Type[Any]] = None,
) -> None:
    """Execute a client request with the given parameters, handling streaming and output.

    Args:
        client: Client instance to use for the request
        request: The ClientRequest to execute
        stream: Whether to stream the response
        model_class: Optional model class for structured outputs
    """
    if not stream:
        # Handle non-streaming execution
        response: ClientResponse[Any] = await client.generate(request=request)

        if model_class and response.is_valid and response.parsed_model:
            print(f"Result: {response.parsed_model}")
            print(response.parsed_model.model_dump_json(indent=2))
        else:
            print(f"Raw content (no model class): {response.raw_content}")
    else:
        # Handle streaming execution
        stream_generator: AsyncGenerator[ClientResponse[Any], None] = client.stream(
            request=request
        )

        async for chunk in stream_generator:
            if model_class and chunk.is_valid and chunk.parsed_model:
                print(f"Valid chunk: {chunk.parsed_model}")
                print(chunk.parsed_model.model_dump_json(indent=2))
            else:
                print(f"Raw chunk content: {chunk.raw_content}")

        # Process the complete content after streaming is done
        full_content = client.provider.stream_history.get_full_content()
        print(f"Full content: {full_content}")

        if model_class:
            try:
                print(f"JSON: {json.loads(full_content)}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Structured full content: {full_content}")
