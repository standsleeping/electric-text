from typing import Dict, Any, Optional, List


def create_payload(
    model: Optional[str],
    default_model: str,
    messages: list[dict[str, str]],
    stream: bool,
    format_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create the API request payload for Ollama.

    Args:
        model: Model override (optional)
        default_model: Default model to use if model is None
        messages: The list of messages to send
        stream: Whether to stream the response
        format_schema: Optional JSON schema for structured output (already converted to dict)
        tools: Optional list of tools to make available to the model

    Returns:
        Dict containing the formatted payload
    """
    payload = {
        "model": model or default_model,
        "messages": messages,
        "stream": stream,
    }

    # Add format if schema is provided (already converted to dict)
    if format_schema is not None:
        payload["format"] = format_schema

    # Add tools if provided
    if tools is not None and len(tools) > 0:
        payload["tools"] = tools

    return payload