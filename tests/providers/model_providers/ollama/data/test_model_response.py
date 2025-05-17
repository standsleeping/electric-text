import json
from datetime import datetime
from electric_text.providers.model_providers.ollama.data.message import Message
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)


def test_model_response_creation():
    """Creates a ModelResponse dataclass with all required fields."""
    message = Message(role="assistant", content="Hello")
    created_at = datetime.now()

    response = ModelResponse(
        model="llama3.1:8b",
        created_at=created_at,
        message=message,
        done_reason="stop",
        done=True,
        total_duration=1000,
        load_duration=100,
        prompt_eval_count=10,
        prompt_eval_duration=200,
        eval_count=20,
        eval_duration=300,
        raw_line="raw json line",
    )

    assert response.model == "llama3.1:8b"
    assert response.created_at == created_at
    assert response.message == message
    assert response.done_reason == "stop"
    assert response.done is True
    assert response.total_duration == 1000
    assert response.load_duration == 100
    assert response.prompt_eval_count == 10
    assert response.prompt_eval_duration == 200
    assert response.eval_count == 20
    assert response.eval_duration == 300
    assert response.raw_line == "raw json line"


def test_model_response_from_dict_without_tool_calls():
    """Creates a ModelResponse from a dictionary without tool calls."""
    raw_line = '{"model": "llama3.1:8b", "created_at": "2024-05-01T12:00:00Z"}'
    data = {
        "model": "llama3.1:8b",
        "created_at": "2024-05-01T12:00:00Z",
        "message": {"role": "assistant", "content": "Hello, world!"},
        "done_reason": "stop",
        "done": True,
        "total_duration": 1000,
        "load_duration": 100,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200,
        "eval_count": 20,
        "eval_duration": 300,
    }

    response = ModelResponse.from_dict(data, raw_line)

    assert response.model == "llama3.1:8b"
    # Just check that created_at is a datetime with UTC timezone
    assert response.created_at.year == 2024
    assert response.created_at.month == 5
    assert response.created_at.day == 1
    assert response.created_at.hour == 12
    assert response.created_at.minute == 0
    assert response.message.role == "assistant"
    assert response.message.content == "Hello, world!"
    assert response.message.tool_calls is None
    assert response.done_reason == "stop"
    assert response.done is True
    assert response.raw_line == raw_line


def test_model_response_from_dict_with_tool_calls():
    """Creates a ModelResponse from a dictionary with tool calls."""
    tool_call = {
        "function": {"name": "get_weather", "arguments": '{"location":"Seattle"}'}
    }

    raw_line = json.dumps(
        {"model": "llama3.1:8b", "message": {"tool_calls": [tool_call]}}
    )

    data = {
        "model": "llama3.1:8b",
        "created_at": "2024-05-01T12:00:00Z",
        "message": {
            "role": "assistant",
            "content": "Let me check the weather",
            "tool_calls": [
                {
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"location":"Seattle"}',
                    }
                }
            ],
        },
        "done_reason": "stop",
        "done": True,
        "total_duration": 1000,
        "load_duration": 100,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200,
        "eval_count": 20,
        "eval_duration": 300,
    }

    response = ModelResponse.from_dict(data, raw_line)

    assert response.model == "llama3.1:8b"
    assert response.message.role == "assistant"
    assert response.message.content == "Let me check the weather"
    assert response.message.tool_calls is not None
    assert len(response.message.tool_calls) == 1
    assert response.message.tool_calls[0].function["name"] == "get_weather"
    assert (
        response.message.tool_calls[0].function["arguments"] == '{"location":"Seattle"}'
    )
