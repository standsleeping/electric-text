import httpx
import json
import pytest
from unittest.mock import AsyncMock, patch

from electric_text.providers.model_providers.ollama import OllamaProvider
from electric_text.providers.data.stream_history import StreamChunkType, StreamHistory
from electric_text.providers.data.provider_request import ProviderRequest


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Error raised when response format is invalid."""

    pass


def create_test_response(message_content, tool_calls=None):
    """Helper function to create a standardized test response JSON.

    Args:
        message_content (str): The content of the assistant's message
        tool_calls (list, optional): List of tool calls to include in the response

    Returns:
        dict: A standardized response JSON matching Ollama's format
    """
    message = {"role": "assistant", "content": message_content}
    if tool_calls:
        message["tool_calls"] = tool_calls

    return {
        "model": "llama3.1:8b",
        "created_at": "2024-05-01T12:00:00Z",
        "message": message,
        "done_reason": "stop",
        "done": True,
        "total_duration": 1000,
        "load_duration": 100,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 200,
        "eval_count": 20,
        "eval_duration": 300,
    }


@pytest.mark.asyncio
async def test_get_client_creates_with_correct_config():
    """Creates an httpx client with the configured timeout and headers."""
    provider = OllamaProvider(timeout=45.0)

    async with provider.get_client() as client:
        assert isinstance(client, httpx.AsyncClient)
        assert client.timeout == httpx.Timeout(45.0)
        assert client.headers["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_get_client_includes_custom_kwargs():
    """Creates a client with additional custom configuration."""
    custom_headers = {"Authorization": "Bearer test"}
    provider = OllamaProvider(headers=custom_headers)

    async with provider.get_client() as client:
        assert client.headers["Authorization"] == "Bearer test"


@pytest.mark.asyncio
async def test_get_client_closes_after_context():
    """Client is properly closed after exiting the context manager."""
    provider = OllamaProvider()
    client = None

    async with provider.get_client() as c:
        client = c
        assert not client.is_closed

    assert client.is_closed


@pytest.mark.asyncio
async def test_generate_completion_successful_response():
    """Successfully parses a complete response from the API."""
    provider = OllamaProvider()

    mock_request = httpx.Request(
        "POST",
        "http://test",
    )

    mock_response = httpx.Response(
        200,
        json=create_test_response("test result"),
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        user_request = ProviderRequest(
            provider_name="ollama",
            prompt_text="test prompt",
            model_name="llama3.1:8b",
            system_messages=["You are a helpful assistant"],
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
        assert result.chunks[0].content == "test result"
        assert result.get_full_content() == "test result"


@pytest.mark.asyncio
async def test_generate_completion_http_error():
    """Returns StreamHistory with HTTP_ERROR chunk when HTTP request fails."""
    provider = OllamaProvider()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        user_request = ProviderRequest(
            provider_name="ollama",
            prompt_text="test prompt",
            model_name="llama3.1:8b",
            system_messages=["You are a helpful assistant"],
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.HTTP_ERROR
        assert result.chunks[0].error == "Complete request failed: Connection failed"
        assert result.chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_stream_yields_chunks():
    """Yields stream history objects containing accumulated chunks."""
    provider = OllamaProvider()

    user_request = ProviderRequest(
        provider_name="ollama",
        prompt_text="Hello",
        model_name="llama3.1:8b",
        system_messages=["You are a helpful assistant"],
    )

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        content=b'{"message": {"content": "chunk1"}}\n{"message": {"content": "chunk2"}}',
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield '{"message": {"content": "chunk1"}}'
        yield '{"message": {"content": "chunk2"}}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        async for history in provider.generate_stream(user_request):
            histories.append(history)

        assert len(histories) == 2

        # Each history is the same object with more chunks
        assert histories[0] is histories[1]  # Same object
        assert len(histories[0].chunks) == 2  # Both chunks present

        # Verify the chunks are correct
        assert histories[0].chunks[0].content == "chunk1"
        assert histories[0].chunks[1].content == "chunk2"

        # Verify the accumulated content
        assert histories[0].get_full_content() == "chunk1chunk2"


@pytest.mark.asyncio
async def test_generate_stream_http_error():
    """Yields StreamHistory with HTTP_ERROR chunk when streaming request fails."""
    provider = OllamaProvider()

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Stream failed")

        user_request = ProviderRequest(
            provider_name="ollama",
            prompt_text="test prompt",
            model_name="llama3.1:8b",
            system_messages=["You are a helpful assistant"],
        )

        histories = []
        async for history in provider.generate_stream(user_request):
            histories.append(history)

        assert len(histories) == 1
        assert isinstance(histories[0], StreamHistory)
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.HTTP_ERROR
        assert histories[0].chunks[0].error == "Stream request failed: Stream failed"
        assert histories[0].chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_stream_invalid_json():
    """Records invalid JSON in stream history instead of raising."""
    provider = OllamaProvider()

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

    async def mock_aiter_lines():
        yield "invalid json"

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        user_request = ProviderRequest(
            provider_name="ollama",
            prompt_text="test prompt",
            model_name="llama3.1:8b",
            system_messages=["You are a helpful assistant"],
        )

        async for history in provider.generate_stream(user_request):
            histories.append(history)

        # Should get one history object with the error chunk
        assert len(histories) == 1
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.PARSE_ERROR
        assert histories[0].chunks[0].raw_line == "invalid json"
        assert histories[0].chunks[0].error is not None


@pytest.mark.asyncio
async def test_generate_completion_with_tools():
    """Successfully handles a response with tool calls."""
    provider = OllamaProvider()

    # Create a mock response with tool calls
    tool_call = {
        "id": "tool_call_1",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"location":"Chicago","unit":"celsius"}',
        },
    }

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        json=create_test_response("I'll check the weather for you.", [tool_call]),
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        # Create a request with tools
        weather_tool = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use",
                        },
                    },
                    "required": ["location"],
                },
            },
        }

        user_request = ProviderRequest(
            provider_name="ollama",
            prompt_text="What's the weather in Chicago?",
            model_name="llama3.1:8b",
            system_messages=["You are a helpful assistant"],
            tools=[weather_tool],
        )

        result = await provider.generate_completion(user_request)

        # Check that tools were included in the payload
        payload = mock_post.call_args[1]["json"]
        assert "tools" in payload
        assert payload["tools"] == [weather_tool]

        # Check that the tool calls were properly parsed in the result
        assert isinstance(result, StreamHistory)

        # Should have at least 3 chunks: tool call, tool call done, and content
        assert len(result.chunks) == 3

        # Content chunk should be included
        assert any(
            chunk.type == StreamChunkType.CONTENT_CHUNK for chunk in result.chunks
        )

        content_chunk = next(
            chunk
            for chunk in result.chunks
            if chunk.type == StreamChunkType.CONTENT_CHUNK
        )

        assert content_chunk.content == "I'll check the weather for you."

        # Tool call chunks should be included
        assert any(
            chunk.type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
            for chunk in result.chunks
        )

        assert any(
            chunk.type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
            for chunk in result.chunks
        )


@pytest.mark.asyncio
async def test_generate_stream_with_tools():
    """Yields stream history objects containing tool call chunks."""
    provider = OllamaProvider()

    # Create a request with tools
    weather_tool = {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use",
                    },
                },
                "required": ["location"],
            },
        },
    }

    user_request = ProviderRequest(
        provider_name="ollama",
        prompt_text="What's the weather in Omaha?",
        model_name="llama3.1:8b",
        system_messages=["You are a helpful assistant"],
        tools=[weather_tool],
    )

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

    tool_call = {
        "id": "tool_call_1",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"location":"Omaha","unit":"celsius"}',
        },
    }

    async def mock_aiter_lines():
        yield '{"message": {"tool_calls": [' + json.dumps(tool_call) + "]}}"
        yield '{"message": {"content": "I\'ll check the weather for you."}, "done": true}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()

        # Check that tools were included in the payload
        histories = []

        async for history in provider.generate_stream(user_request):
            histories.append(history)

        # Check that payload contains tools
        payload = mock_stream.call_args[1]["json"]
        assert "tools" in payload
        assert payload["tools"] == [weather_tool]

        # We should have accumulated several history objects:
        # 1. After tool call chunk
        # 2. After tool call done
        # 3. After content chunk
        # 4. After completion end
        assert len(histories) == 4

        # All histories should be the same object with more chunks
        assert histories[0] is histories[-1]

        # First chunk should be the function call
        assert (
            histories[0].chunks[0].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DELTA
        )

        # Second chunk should mark function call as done
        assert (
            histories[1].chunks[1].type == StreamChunkType.FUNCTION_CALL_ARGUMENTS_DONE
        )

        # Third chunk should be the text content
        assert histories[2].chunks[2].type == StreamChunkType.CONTENT_CHUNK
        assert histories[2].chunks[2].content == "I'll check the weather for you."

        # Last chunk should be completion end
        assert histories[3].chunks[3].type == StreamChunkType.COMPLETION_END
