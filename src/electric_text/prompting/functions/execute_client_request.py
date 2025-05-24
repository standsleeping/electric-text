from typing import Any, AsyncGenerator, Optional, Type

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.logging import get_logger
from electric_text.formatting.functions.format_non_streaming_response import (
    format_non_streaming_response,
)
from electric_text.formatting.functions.format_streaming_chunk import (
    format_streaming_chunk,
)
from electric_text.formatting.functions.format_streaming_final_output import (
    format_streaming_final_output,
)

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

    # Handle non-streaming execution
    if not stream:
        response: ClientResponse[Any] = await client.generate(request=request)
        formatted_output = format_non_streaming_response(
            content=response.get_formatted_content(),
            is_valid=response.is_valid,
            parsed_model=response.parsed_model,
            model_class=model_class,
        )
        print(formatted_output)
        return

    # Handle streaming execution - choose appropriate streaming method
    if request.response_model is not None:
        # Use structured streaming for requests with response models
        stream_generator: AsyncGenerator[ClientResponse[Any], None] = (
            client.stream_structured(request=request)
        )
    else:
        # Use regular streaming for unstructured requests
        stream_generator: AsyncGenerator[ClientResponse[Any], None] = client.stream(
            request=request
        )

    # Keep track of the last chunk for final output
    last_chunk = None

    async for chunk in stream_generator:
        formatted_chunk = format_streaming_chunk(
            content=chunk.get_formatted_content(),
            is_valid=chunk.is_valid,
            parsed_model=chunk.parsed_model,
            model_class=model_class,
        )

        print(formatted_chunk)

        # Keep the last chunk to get final content
        last_chunk = chunk

    # Process the complete content from the last chunk
    if last_chunk:
        if request.response_model is not None:
            # For structured responses, use the last chunk as the final result
            formatted_final_output = format_non_streaming_response(
                content=last_chunk.get_formatted_content(),
                is_valid=last_chunk.is_valid,
                parsed_model=last_chunk.parsed_model,
                model_class=model_class,
            )
        else:
            # For unstructured responses, extract content from content blocks
            full_content = ""
            full_content = last_chunk.get_formatted_content()
            formatted_final_output = format_streaming_final_output(
                full_content=full_content,
                model_class=model_class,
            )

        print(formatted_final_output)
