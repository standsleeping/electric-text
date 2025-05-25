import logging
from typing import AsyncGenerator

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from pydantic import BaseModel
from electric_text.logging import get_logger

logger: logging.Logger = get_logger(__name__)


async def execute_client_request[Schema: BaseModel](
    *,
    client: Client,
    request: ClientRequest[Schema],
    stream: bool = False,
) -> None:
    """Execute a client request with the given parameters, handling streaming and output.

    Args:
        client: Client instance to use for the request
        request: The ClientRequest to execute
        stream: Whether to stream the response
        model_class: Optional model class for structured outputs
    """

    if stream:
        req: ClientRequest[Schema] = request
        gen: AsyncGenerator[ClientResponse[Schema], None] = client.stream(request=req)
        async for part in gen:
            print(part)
            print("--------------------------------")

    else:
        full_response: ClientResponse[Schema] = await client.generate(request=request)
        print(full_response)
