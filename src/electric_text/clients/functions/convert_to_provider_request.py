from electric_text.clients.data.client_request import ClientRequest
from electric_text.providers.data.provider_request import ProviderRequest


def convert_to_provider_request(client_request: ClientRequest) -> ProviderRequest:
    """Convert a ClientRequest to a ProviderRequest.

    Args:
        client_request: The client request to convert

    Returns:
        The provider request
    """
    system_messages = (
        [fragment.text for fragment in client_request.prompt.system_message]
        if client_request.prompt.system_message
        else None
    )

    return ProviderRequest(
        provider_name=client_request.provider_name,
        model_name=client_request.model_name,
        prompt_text=client_request.prompt.prompt,
        system_messages=system_messages,
        tools=client_request.tools,
        response_model=client_request.response_model,
        max_tokens=client_request.max_tokens,
    )
