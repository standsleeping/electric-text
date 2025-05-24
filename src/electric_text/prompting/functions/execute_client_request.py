from typing import Any, AsyncGenerator, Optional, Type

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.logging import get_logger
from electric_text.prompting.functions.format_non_streaming_response import (
    format_non_streaming_response,
)
from electric_text.prompting.functions.format_streaming_chunk import (
    format_streaming_chunk,
)
from electric_text.prompting.functions.format_streaming_final_output import (
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
            response=response,
            model_class=model_class,
        )
        print(formatted_output)
        return

    # Handle streaming execution
    stream_generator: AsyncGenerator[ClientResponse[Any], None] = client.stream(
        request=request
    )

    async for chunk in stream_generator:
        formatted_chunk = format_streaming_chunk(
            chunk=chunk,
            model_class=model_class,
        )
        print(formatted_chunk)

    # Process the complete content after streaming is done
    full_content = client.provider.stream_history.get_full_content()
    formatted_final_output = format_streaming_final_output(
        full_content=full_content,
        model_class=model_class,
    )
    print(formatted_final_output)
