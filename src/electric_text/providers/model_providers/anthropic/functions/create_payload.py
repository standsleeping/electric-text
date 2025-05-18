from typing import Dict, Any, Optional, List


def create_payload(
    model: Optional[str],
    default_model: str,
    messages: list[dict[str, str]],
    stream: bool,
    max_tokens: Optional[int] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create the API request payload for Anthropic.

    Args:
        model: Model override (optional)
        default_model: Default model to use if model is None
        messages: The list of messages to send
        stream: Whether to stream the response
        max_tokens: Maximum number of tokens to generate (optional)
        tools: Optional list of tools to make available to the model

    Returns:
        Dict containing the formatted payload
    """
    payload = {
        "model": model or default_model,
        "messages": messages,
        "stream": stream,
    }

    # Use provided max_tokens or default to 4096
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    else:
        payload["max_tokens"] = 4096

    # Add tools if provided and not empty
    if tools and len(tools) > 0:
        payload["tools"] = tools

    return payload