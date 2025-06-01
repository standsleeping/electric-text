import json
import logging
from typing import AsyncGenerator

from electric_text.clients import Client
from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.client_response import ClientResponse
from electric_text.clients.data.validation_model import ValidationModel
from electric_text.logging import get_logger
from electric_text.prompting.data.system_output import SystemOutput
from electric_text.prompting.functions.output_conversion.client_response_to_system_output import (
    client_response_to_system_output,
)
from electric_text.prompting.functions.output_conversion.system_output_to_dict import (
    system_output_to_dict,
)

logger: logging.Logger = get_logger(__name__)


async def execute_client_request[Schema: ValidationModel](
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
            stream_output: SystemOutput = client_response_to_system_output(part)
            output_dict = system_output_to_dict(stream_output)
            print(json.dumps(output_dict))

    else:
        full_response: ClientResponse[Schema] = await client.generate(request=request)
        system_output: SystemOutput = client_response_to_system_output(full_response)
        output_dict = system_output_to_dict(system_output)
        print(json.dumps(output_dict))
