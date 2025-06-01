import logging
from typing import AsyncGenerator, Union

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.clients.data.validation_model import ValidationModel
from electric_text.logging import get_logger
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.functions.output_conversion.client_response_to_system_output import (
    client_response_to_system_output,
)

logger: logging.Logger = get_logger(__name__)


async def execute_client_request_with_return[Schema: ValidationModel](
    *,
    client: Client,
    request: ClientRequest[Schema],
    stream: bool = False,
) -> Union[SystemOutput, AsyncGenerator[SystemOutput, None]]:
    """Execute a client request with the given parameters and return the result.

    Args:
        client: Client instance to use for the request
        request: The ClientRequest to execute
        stream: Whether to stream the response

    Returns:
        SystemOutput if stream=False, AsyncGenerator[SystemOutput, None] if stream=True
    """

    if stream:

        async def stream_generator() -> AsyncGenerator[SystemOutput, None]:
            req: ClientRequest[Schema] = request
            gen: AsyncGenerator[ClientResponse[Schema], None] = client.stream(
                request=req
            )

            async for part in gen:
                yield client_response_to_system_output(part)

        return stream_generator()

    else:
        full_response: ClientResponse[Schema] = await client.generate(request=request)
        return client_response_to_system_output(full_response)
