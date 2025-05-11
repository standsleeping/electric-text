from typing import Optional, Type, Any, List, Dict

from electric_text.providers.data.user_request import UserRequest
from electric_text.clients import build_simple_prompt, convert_prompt_to_messages


def create_user_request(
    *,
    model_name: str,
    provider_name: str,
    response_model: Optional[Type[Any]] = None,
    stream: bool = False,
    system_message: Optional[str] = None,
    text_input: Optional[str] = None,
    max_tokens: Optional[int] = None,
    tool_boxes: Optional[List[str]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
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
        max_tokens: Maximum number of tokens to generate
        tool_boxes: List of tool box names to use
        tools: Pre-loaded tools (if not provided, will be loaded from tool_boxes)

    Returns:
        A configured UserRequest instance
    """
    sys_msg = system_message or "You are a helpful assistant."
    txt_input = text_input or ""
    prompt = build_simple_prompt(sys_msg, txt_input)
    messages = convert_prompt_to_messages(prompt)

    # Process tool boxes and tools
    tool_box_list = tool_boxes or []

    return UserRequest(
        messages=messages,
        model=model_name,
        provider_name=provider_name,
        response_model=response_model,
        stream=stream,
        max_tokens=max_tokens,
        tool_boxes=tool_box_list,
        tools=tools,
    )
