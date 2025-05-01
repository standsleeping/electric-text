from typing import List, Dict, Optional, Type, Any, Union

from electric_text.clients.data.user_request import UserRequest
from electric_text.clients import build_simple_prompt, convert_prompt_to_messages


def create_user_request(
    *,
    model_name: str,
    provider_name: str,
    response_model: Optional[Type[Any]] = None,
    stream: bool = False,
    system_message: Optional[str] = None,
    text_input: Optional[str] = None,
) -> UserRequest:
    """Create a UserRequest instance with the given parameters.

    Args:
        model_name: The model name to use
        provider_name: The provider name (e.g., "anthropic", "openai")
        response_model: Optional response model for structured output
        stream: Whether to stream the response
        messages: Pre-built messages (mutually exclusive with system_message + text_input)
        system_message: System message content (used with text_input)
        text_input: User text input (used with system_message)

    Returns:
        A configured UserRequest instance
    """
    sys_msg = system_message or ""
    txt_input = text_input or ""
    prompt = build_simple_prompt(sys_msg, txt_input)
    messages = convert_prompt_to_messages(prompt)

    return UserRequest(
        messages=messages,
        model=model_name,
        provider_name=provider_name,
        response_model=response_model,
        stream=stream,
    )
