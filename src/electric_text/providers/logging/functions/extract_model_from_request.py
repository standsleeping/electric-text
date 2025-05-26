import json
import httpx


def extract_model_from_request(
    request: httpx.Request, default_model: str | None
) -> str | None:
    """Extract model name from httpx request.

    Args:
        request: The httpx request
        default_model: Default model name to use

    Returns:
        Extracted or default model name
    """
    if default_model:
        return default_model

    # Try to extract from request content if it's JSON
    if request.content:
        try:
            json_data = json.loads(request.content.decode())
            if isinstance(json_data, dict):
                model = json_data.get("model")
                return str(model) if model else None
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

    return None
