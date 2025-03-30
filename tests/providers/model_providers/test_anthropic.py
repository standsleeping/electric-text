import json
import httpx
import pytest
from typing import Any
from unittest.mock import AsyncMock, patch

from electric_text.providers.model_providers.anthropic import (
    AnthropicProvider,
    FormatError,
)
from electric_text.providers.stream_history import StreamChunkType, StreamHistory


@pytest.fixture
def test_schema():
    """Common schema used across tests."""
    return {"type": "object", "properties": {"value": {"type": "string"}}}


class FakeResponse:
    """Test response type for schema validation."""

    def __init__(self, **kwargs: Any) -> None:
        self.value = kwargs.get("value")


def test_register_schema_stores_schema(test_schema):
    """A schema can be registered and stored for a response type."""
    provider = AnthropicProvider(api_key="test_key")

    provider.register_schema(FakeResponse, test_schema)

    assert provider.format_schemas[FakeResponse] == test_schema


def test_register_schema_multiple_types():
    """Multiple schemas can be registered for different response types."""
    provider = AnthropicProvider(api_key="test_key")
    schema1 = {"type": "object", "properties": {"test1": {"type": "string"}}}
    schema2 = {"type": "object", "properties": {"test2": {"type": "number"}}}

    class FakeResponse1:
        def __init__(self, **kwargs: Any) -> None:
            pass

    class FakeResponse2:
        def __init__(self, **kwargs: Any) -> None:
            pass

    provider.register_schema(FakeResponse1, schema1)
    provider.register_schema(FakeResponse2, schema2)

    assert provider.format_schemas[FakeResponse2] == schema2


def test_constructor_with_defaults():
    """Constructor uses reasonable defaults."""
    provider = AnthropicProvider(api_key="test_key")

    assert provider.base_url == "https://api.anthropic.com/v1/messages"
    assert provider.default_model == "claude-3-sonnet-20240229"
    assert provider.timeout == 30.0
    assert provider.api_version == "2023-06-01"
    assert provider.client_kwargs["headers"]["x-api-key"] == "test_key"
    assert provider.client_kwargs["headers"]["anthropic-version"] == "2023-06-01"


def test_constructor_with_custom_values():
    """Constructor accepts custom configuration values."""
    provider = AnthropicProvider(
        api_key="custom_key",
        base_url="https://custom.api/v1",
        default_model="custom-model",
        api_version="custom-version",
        timeout=60.0,
    )

    assert provider.base_url == "https://custom.api/v1"
    assert provider.default_model == "custom-model"
    assert provider.timeout == 60.0
    assert provider.api_version == "custom-version"
    assert provider.client_kwargs["headers"]["x-api-key"] == "custom_key"
    assert provider.client_kwargs["headers"]["anthropic-version"] == "custom-version"


def test_create_payload_with_registered_schema(test_schema):
    """Creates a payload with a registered schema."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "system", "content": "preserved-system-message"},
        {"role": "user", "content": "Hello"},
    ]

    payload = provider.create_payload(
        messages,
        FakeResponse,
        None,
        False,
    )

    expected_system_message = "preserved-system-message"
    assert payload["model"] == "claude-3-sonnet-20240229"
    assert payload["messages"][0]["role"] == "user" # NOTE: we change this create_payload()
    assert payload["messages"][0]["content"] == expected_system_message
    assert payload["messages"][1]["content"] == "Acknowledged. I will respond with JSON." # NOTE: we add this create_payload()
    assert payload["stream"] is False
    assert payload["max_tokens"] == 4096


def test_create_payload_with_model_override(test_schema):
    """Creates a payload with a custom model specified."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "user", "content": "Hello"},
    ]

    payload = provider.create_payload(
        messages,
        FakeResponse,
        "claude-3-haiku-20240307",
        True,
    )

    assert payload["model"] == "claude-3-haiku-20240307"
    assert payload["stream"] is True
    assert payload["messages"][0]["role"] == "user" # NOTE: we change this create_payload()
    assert payload["messages"][0]["content"] == "Hello"
    assert payload["messages"][1]["role"] == "assistant" # NOTE: we add this create_payload()
    assert payload["messages"][1]["content"] == "Acknowledged. I will respond with JSON."


def test_create_payload_without_schema_raises_error():
    """Creating a payload without a registered schema raises FormatError."""
    provider = AnthropicProvider(api_key="test_key")

    with pytest.raises(FormatError, match="No schema registered for type FakeResponse"):
        provider.create_payload("test prompt", FakeResponse, None, False)


@pytest.mark.asyncio
async def test_get_client_creates_with_correct_config():
    """Creates an httpx client with the configured timeout and headers."""
    provider = AnthropicProvider(api_key="test_key", timeout=45.0)

    async with provider.get_client() as client:
        assert isinstance(client, httpx.AsyncClient)
        assert client.timeout == httpx.Timeout(45.0)
        assert client.headers["Content-Type"] == "application/json"
        assert client.headers["x-api-key"] == "test_key"
        assert client.headers["anthropic-version"] == "2023-06-01"


@pytest.mark.asyncio
async def test_get_client_closes_after_context():
    """Client is properly closed after exiting the context manager."""
    provider = AnthropicProvider(api_key="test_key")
    client = None

    async with provider.get_client() as c:
        client = c
        assert not client.is_closed

    assert client.is_closed


@pytest.mark.asyncio
async def test_generate_completion_successful_response(test_schema):
    """Successfully parses a complete response from the API."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    RESULT = {"value": "test result"}
    RESPONSE_CONTENT = {"content": [{"text": json.dumps(RESULT), "type": "text"}]}

    mock_request = httpx.Request(
        "POST",
        "http://test",
    )

    mock_response = httpx.Response(
        200,
        json=RESPONSE_CONTENT,
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await provider.generate_completion(
            [{"role": "user", "content": "test prompt"}], FakeResponse
        )

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
        assert result.chunks[0].content == json.dumps(RESULT)
        assert result.get_full_content() == json.dumps(RESULT)


@pytest.mark.asyncio
async def test_generate_completion_http_error(test_schema):
    """Returns StreamHistory with HTTP_ERROR chunk when HTTP request fails."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        result = await provider.generate_completion(
            [{"role": "user", "content": "test prompt"}], FakeResponse
        )

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.HTTP_ERROR
        assert result.chunks[0].error == "Complete request failed: Connection failed"
        assert result.chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_completion_missing_content(test_schema):
    """Returns StreamHistory with FORMAT_ERROR chunk when response is missing required content."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        json={
            # Missing content field
        },
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await provider.generate_completion(
            [{"role": "user", "content": "test prompt"}], FakeResponse
        )

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert "Failed to parse response" in result.chunks[0].error
        assert result.chunks[0].raw_line == "{}"


@pytest.mark.asyncio
async def test_generate_stream_yields_chunks(test_schema):
    """Yields stream history objects containing accumulated chunks."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield 'data: {"delta": {"text": "Hello"}, "type": "content_block_delta"}'
        yield 'data: {"delta": {"text": " world"}, "type": "content_block_delta"}'
        yield 'data: {"type": "message_stop"}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        async for history in provider.generate_stream(messages, FakeResponse):
            histories.append(history)

        # We should get three history objects (same object, updated)
        assert len(histories) == 3
        assert histories[0] is histories[1] is histories[2]  # All same object

        # Final history should have all chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 3

        # First chunk should be the first part of content
        assert final_history.chunks[0].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[0].content == "Hello"

        # Second chunk should be the second part of content
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == " world"

        # Third chunk should be the completion marker
        assert final_history.chunks[2].type == StreamChunkType.COMPLETION_END

        # Full content should combine all content chunks
        assert final_history.get_full_content() == "Hello world"


@pytest.mark.asyncio
async def test_generate_stream_http_error(test_schema):
    """Returns StreamHistory with HTTP_ERROR chunk when stream request fails."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "user", "content": "Hello"},
    ]

    # Mock the get_client method to raise an exception
    with patch.object(provider, "get_client") as mock_get_client:
        mock_get_client.side_effect = httpx.HTTPError("Connection failed")

        histories = []
        async for history in provider.generate_stream(messages, FakeResponse):
            histories.append(history)

        assert len(histories) == 1
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.HTTP_ERROR
        assert (
            histories[0].chunks[0].error == "Stream request failed: Connection failed"
        )


@pytest.mark.asyncio
async def test_generate_stream_json_error(test_schema):
    """Records JSON errors in stream history."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "user", "content": "Hello"},
    ]

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield "data: invalid json"

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        async for history in provider.generate_stream(messages, FakeResponse):
            histories.append(history)

        # We should get one history object with the error chunk
        assert len(histories) == 1
        final_history = histories[0]
        assert len(final_history.chunks) == 1

        # The chunk should be a parse error
        assert final_history.chunks[0].type == StreamChunkType.PARSE_ERROR
        assert final_history.chunks[0].raw_line == "data: invalid json"
        assert (
            "JSONDecodeError" in final_history.chunks[0].error
            or "Expecting value" in final_history.chunks[0].error
        )


@pytest.mark.asyncio
async def test_generate_stream_api_error(test_schema):
    """Records API errors in stream history."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "user", "content": "Hello"},
    ]

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield 'data: {"error": {"message": "API rate limit exceeded", "type": "rate_limit_error"}}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        async for history in provider.generate_stream(messages, FakeResponse):
            histories.append(history)

        # We should get one history object with the error chunk
        assert len(histories) == 1
        final_history = histories[0]
        assert len(final_history.chunks) == 1

        # The chunk should be a FORMAT_ERROR since we changed API_ERROR to FORMAT_ERROR
        assert final_history.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert final_history.chunks[0].error == "API rate limit exceeded"


@pytest.mark.asyncio
async def test_generate_stream_empty_line(test_schema):
    """Skips empty lines in stream history."""
    provider = AnthropicProvider(api_key="test_key")
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "user", "content": "Hello"},
    ]

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield ""
        yield " "
        yield 'data: {"delta": {"text": "Hello"}, "type": "content_block_delta"}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        histories = []

        async for history in provider.generate_stream(messages, FakeResponse):
            histories.append(history)

        # We should only get one history object since empty lines are skipped
        assert len(histories) == 1
        final_history = histories[0]

        # Should only have the content chunk
        assert len(final_history.chunks) == 1
        assert final_history.chunks[0].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[0].content == "Hello"
