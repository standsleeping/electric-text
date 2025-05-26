import json
import httpx

from electric_text.providers.logging.functions.extract_model_from_request import (
    extract_model_from_request,
)


def test_returns_default_model_when_provided():
    """Returns default model when provided."""
    request = httpx.Request("POST", "https://api.example.com")
    result = extract_model_from_request(request, "gpt-4")
    assert result == "gpt-4"


def test_extracts_model_from_json_request_body():
    """Extracts model from JSON request body."""
    json_data = {"model": "claude-3-sonnet", "messages": []}
    content = json.dumps(json_data).encode()
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result == "claude-3-sonnet"


def test_returns_none_for_non_json_request_body():
    """Returns None for non-JSON request body."""
    content = b"not json content"
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result is None


def test_returns_none_for_empty_request_content():
    """Returns None for empty request content."""
    request = httpx.Request("POST", "https://api.example.com")
    result = extract_model_from_request(request, None)
    assert result is None


def test_returns_none_for_malformed_json():
    """Returns None for malformed JSON."""
    content = b'{"model": "claude-3-sonnet", "incomplete":'
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result is None


def test_returns_none_when_model_key_missing():
    """Returns None when model key missing from JSON."""
    json_data = {"messages": [], "temperature": 0.7}
    content = json.dumps(json_data).encode()
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result is None


def test_converts_non_string_model_to_string():
    """Converts non-string model values to string."""
    json_data = {"model": 123, "messages": []}
    content = json.dumps(json_data).encode()
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result == "123"


def test_returns_none_for_non_dict_json():
    """Returns None for valid JSON that is not a dictionary."""
    content = json.dumps(["not", "a", "dict"]).encode()
    request = httpx.Request("POST", "https://api.example.com", content=content)
    result = extract_model_from_request(request, None)
    assert result is None
