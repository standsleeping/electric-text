from typing import Dict, Any, Optional, List
from electric_text.providers.model_providers.openai.functions.set_text_format import (
    set_text_format,
)


def create_payload(
    model: Optional[str],
    default_model: str,
    messages: list[dict[str, str]],
    stream: bool,
    format_schema: Optional[Dict[str, Any]] = None,
    strict_schema: bool = True,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Create the API request payload for OpenAI.

    Args:
        model: Model override (optional)
        default_model: Default model to use if model is None
        messages: The list of messages to send
        stream: Whether to stream the response
        format_schema: Optional JSON schema for structured outputs
        strict_schema: Whether to enforce strict schema validation (default: True)
        tools: Optional list of tools to make available to the model

    Returns:
        Dict containing the formatted payload
    """
    payload = {
        "model": model or default_model,
        "input": messages,
        "stream": stream,
    }

    if format_schema:
        payload["text"] = set_text_format(format_schema, strict=strict_schema)

    if tools:
        payload["tools"] = tools

    return payload
