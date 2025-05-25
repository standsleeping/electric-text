from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.default_output_schema import DefaultOutputSchema
from electric_text.providers.data.provider_request import ProviderRequest
from typing import Any, List, Optional


def convert_to_provider_request(client_request: ClientRequest[Any]) -> ProviderRequest:
    """Convert a ClientRequest to a ProviderRequest.

    Args:
        client_request: The client request to convert

    Returns:
        The provider request
    """
    system_messages: Optional[List[str]] = None
    if client_request.prompt.system_message is not None:
        system_messages = [fragment.text for fragment in client_request.prompt.system_message]

    has_custom_schema = (
        client_request.output_schema is not None and 
        client_request.output_schema is not DefaultOutputSchema
    )

    return ProviderRequest(
        provider_name=client_request.provider_name,
        model_name=client_request.model_name,
        prompt_text=client_request.prompt.prompt,
        system_messages=system_messages,
        tools=client_request.tools,
        output_schema=client_request.output_schema,
        max_tokens=client_request.max_tokens,
        has_custom_output_schema=has_custom_schema,
    )
