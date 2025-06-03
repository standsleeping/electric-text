from electric_text.providers.logging.functions.http_log_entry_to_dict import (
    http_log_entry_to_dict,
)
from tests.fixtures import sample_http_log_entry, minimal_http_log_entry


def test_converts_complete_log_entry_to_dict():
    """Converts complete log entry to dictionary."""
    result = http_log_entry_to_dict(sample_http_log_entry())

    expected = {
        "timestamp": "2024-01-01T12:00:00Z",
        "method": "POST",
        "url": "https://api.example.com/chat",
        "request": {
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer token",
            },
            "body": {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
        "response": {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"choices": [{"message": {"content": "Hi there!"}}]},
        },
        "duration_ms": 1222.2,
        "provider": "openai",
        "model": "gpt-4",
        "error": None,
    }

    assert result == expected


def test_converts_minimal_log_entry_to_dict():
    """Converts minimal log entry with None values to dictionary."""
    result = http_log_entry_to_dict(minimal_http_log_entry())

    expected = {
        "timestamp": "2024-01-01T12:00:00Z",
        "method": "GET",
        "url": "https://api.example.com/chat",
        "request": {"headers": {}, "body": None},
        "response": {"status": 404, "headers": {}, "body": None},
        "duration_ms": 100.0,
        "provider": None,
        "model": None,
        "error": "HTTP 404",
    }

    assert result == expected


def test_dict_structure_matches_expected_format():
    """Dictionary structure matches expected format."""
    result = http_log_entry_to_dict(sample_http_log_entry())

    expected_keys = {
        "timestamp",
        "method",
        "url",
        "request",
        "response",
        "duration_ms",
        "provider",
        "model",
        "error",
    }
    assert set(result.keys()) == expected_keys


def test_nested_request_response_structure():
    """Nested request/response structure is correct."""
    result = http_log_entry_to_dict(sample_http_log_entry())

    request_dict = result["request"]
    response_dict = result["response"]

    assert isinstance(request_dict, dict)
    assert isinstance(response_dict, dict)
    assert set(request_dict.keys()) == {"headers", "body"}
    assert set(response_dict.keys()) == {"status", "headers", "body"}
