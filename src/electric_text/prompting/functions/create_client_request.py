from typing import Any, List, Optional, Type

from electric_text.clients.data.client_request import ClientRequest
from electric_text.clients.data.prompt import Prompt
from electric_text.clients.data.template_fragment import TemplateFragment
from electric_text.clients.data.validation_model import ValidationModel


def create_client_request[OutputSchema: ValidationModel](
    *,
    provider_name: str,
    model_name: str,
    text_input: str,
    system_message: str = "You are a helpful assistant.",
    tools: Optional[List[Any]] = None,
    max_tokens: Optional[int] = None,
    output_schema: Type[OutputSchema],
) -> ClientRequest[OutputSchema]:
    """Create a client request for prompt execution.

    Args:
        provider_name: Name of the provider to use
        model_name: Name of the model to use
        text_input: Input text for the prompt
        system_message: System message to use (default is "You are a helpful assistant.")
        tools: Optional list of tools to use
        max_tokens: Optional maximum number of tokens for completion
        output_schema: Optional response model class for structured outputs

    Returns:
        ClientRequest configured with the provided parameters
    """
    prompt: Prompt = Prompt(
        system_message=[TemplateFragment(text=system_message)],
        prompt=text_input,
    )

    return ClientRequest(
        provider_name=provider_name,
        model_name=model_name,
        prompt=prompt,
        tools=tools,
        max_tokens=max_tokens,
        output_schema=output_schema,
    )
