import json
from datetime import datetime
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.functions.process_tool_calls import (
    process_tool_calls,
)
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)
from electric_text.providers.model_providers.ollama.data.message import Message
from electric_text.providers.model_providers.ollama.data.tool_call import ToolCall


def test_process_tool_calls_with_no_tool_calls():
    """Returns empty list when no tool calls are present."""
    message = Message(role="assistant", content="Hello, world!")

    response = ModelResponse(
        model="llama3.1:8b",
        created_at=datetime.now(),
        message=message,
        done_reason="",
        done=False,
        total_duration=100,
        load_duration=10,
        prompt_eval_count=5,
        prompt_eval_duration=20,
        eval_count=10,
        eval_duration=30,
        raw_line="{}",
    )

    chunks = process_tool_calls(response)

    assert isinstance(chunks, list)
    assert len(chunks) == 0


def test_process_tool_calls_with_single_tool_call():
    """Creates appropriate chunks for a single tool call."""
    function_data = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}

    tool_call = ToolCall(function=function_data)
    message = Message(
        role="assistant", content="Let me check the weather", tool_calls=[tool_call]
    )

    raw_line = json.dumps({"message": {"tool_calls": [{"function": function_data}]}})

    response = ModelResponse(
        model="llama3.1:8b",
        created_at=datetime.now(),
        message=message,
        done_reason="",
        done=False,
        total_duration=100,
        load_duration=10,
        prompt_eval_count=5,
        prompt_eval_duration=20,
        eval_count=10,
        eval_duration=30,
        raw_line=raw_line,
    )

    chunks = process_tool_calls(response)

    assert len(chunks) == 2

    # First chunk should be the function call
    assert chunks[0].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert chunks[0].parsed_data == function_data
    assert json.loads(chunks[0].content) == function_data

    # Second chunk should be function call done
    assert chunks[1].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
    assert chunks[1].content == ""
    assert json.loads(chunks[1].parsed_data["tool_calls"]) == [function_data]


def test_process_tool_calls_with_multiple_tool_calls():
    """Creates appropriate chunks for multiple tool calls."""
    function_data_1 = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}

    function_data_2 = {"name": "get_time", "arguments": '{"timezone":"PST"}'}

    tool_call_1 = ToolCall(function=function_data_1)
    tool_call_2 = ToolCall(function=function_data_2)

    message = Message(
        role="assistant",
        content="Let me check the information",
        tool_calls=[tool_call_1, tool_call_2],
    )

    raw_line = json.dumps(
        {
            "message": {
                "tool_calls": [
                    {"function": function_data_1},
                    {"function": function_data_2},
                ]
            }
        }
    )

    response = ModelResponse(
        model="llama3.1:8b",
        created_at=datetime.now(),
        message=message,
        done_reason="",
        done=False,
        total_duration=100,
        load_duration=10,
        prompt_eval_count=5,
        prompt_eval_duration=20,
        eval_count=10,
        eval_duration=30,
        raw_line=raw_line,
    )

    chunks = process_tool_calls(response)

    assert len(chunks) == 3

    # First chunk should be for the first function call
    assert chunks[0].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert chunks[0].parsed_data == function_data_1

    # Second chunk should be for the second function call
    assert chunks[1].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert chunks[1].parsed_data == function_data_2

    # Last chunk should mark all function calls as done
    assert chunks[2].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
    assert json.loads(chunks[2].parsed_data["tool_calls"]) == [
        function_data_1,
        function_data_2,
    ]
