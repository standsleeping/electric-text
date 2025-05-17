from datetime import datetime
from electric_text.providers.data.stream_history import StreamHistory
from electric_text.providers.data.stream_chunk_type import StreamChunkType
from electric_text.providers.model_providers.ollama.functions.process_completion_response import (
    process_completion_response,
)
from electric_text.providers.model_providers.ollama.data.model_response import (
    ModelResponse,
)
from electric_text.providers.model_providers.ollama.data.message import Message
from electric_text.providers.model_providers.ollama.data.tool_call import ToolCall


def test_process_completion_response_with_content_only():
    """Processes a response with only content into a StreamHistory."""
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

    history = StreamHistory()
    result = process_completion_response(response, history)

    # Should be the same history object
    assert result is history

    # Should have one content chunk
    assert len(result.chunks) == 1
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[0].content == "Hello, world!"


def test_process_completion_response_with_tool_calls_only():
    """Processes a response with only tool calls into a StreamHistory."""
    function_data = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}

    tool_call = ToolCall(function=function_data)
    message = Message(role="assistant", content="", tool_calls=[tool_call])

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

    history = StreamHistory()
    result = process_completion_response(response, history)

    # Should be the same history object
    assert result is history

    # Should have two chunks: tool call and tool call done
    assert len(result.chunks) == 2
    assert result.chunks[0].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert result.chunks[1].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE


def test_process_completion_response_with_content_and_tool_calls():
    """Processes a response with both content and tool calls into a StreamHistory."""
    function_data = {"name": "get_weather", "arguments": '{"location":"Seattle"}'}

    tool_call = ToolCall(function=function_data)
    message = Message(
        role="assistant", content="Let me check the weather", tool_calls=[tool_call]
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
        raw_line="{}",
    )

    history = StreamHistory()
    result = process_completion_response(response, history)

    # Should be the same history object
    assert result is history

    # Should have three chunks: content, tool call, and tool call done
    assert len(result.chunks) == 3
    assert result.chunks[0].type == StreamChunkType.CONTENT_CHUNK
    assert result.chunks[0].content == "Let me check the weather"
    assert result.chunks[1].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
    assert result.chunks[2].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
