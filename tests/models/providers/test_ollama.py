import json
import httpx
import pytest
from typing import Any
from unittest.mock import AsyncMock, patch

from models.providers.ollama import OllamaProvider, FormatError, APIError
from models.stream_history import StreamChunkType


@pytest.fixture
def test_schema():
    """Common schema used across tests."""
    return {"type": "object", "properties": {"value": {"type": "string"}}}


class TestResponse:
    def __init__(self, **kwargs: Any) -> None:
        self.value = kwargs.get("value")


def test_register_schema_stores_schema(test_schema):
    """A schema can be registered and stored for a response type."""
    provider = OllamaProvider()

    provider.register_schema(TestResponse, test_schema)

    assert provider.format_schemas[TestResponse] == test_schema


def test_register_schema_multiple_types():
    """Multiple schemas can be registered for different response types."""
    provider = OllamaProvider()
    schema1 = {"type": "object", "properties": {"test1": {"type": "string"}}}
    schema2 = {"type": "object", "properties": {"test2": {"type": "number"}}}

    class TestResponse1:
        def __init__(self, **kwargs: Any) -> None:
            pass

    class TestResponse2:
        def __init__(self, **kwargs: Any) -> None:
            pass

    provider.register_schema(TestResponse1, schema1)
    provider.register_schema(TestResponse2, schema2)

    assert provider.format_schemas[TestResponse2] == schema2


def test_create_payload_with_registered_schema(test_schema):
    """Creates a payload with a registered schema."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    payload = provider.create_payload(
        messages,
        TestResponse,
        None,
        False,
    )

    assert payload == {
        "model": "llama3.1:8b",
        "messages": messages,
        "stream": False,
        "format": test_schema,
    }


def test_create_payload_with_model_override(test_schema):
    """Creates a payload with a custom model specified."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    payload = provider.create_payload(
        "test prompt",
        TestResponse,
        "custom-model",
        True,
    )

    assert payload["model"] == "custom-model"


def test_create_payload_without_schema_raises_error():
    """Creating a payload without a registered schema raises FormatError."""
    provider = OllamaProvider()

    with pytest.raises(FormatError, match="No schema registered for type TestResponse"):
        provider.create_payload("test prompt", TestResponse, None, False)


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
async def test_query_complete_successful_response(test_schema):
    """Successfully parses a complete response from the API."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    RESULT = {"value": "test result"}

    mock_request = httpx.Request(
        "POST",
        "http://test",
    )

    mock_response = httpx.Response(
        200,
        json={"message": {"content": json.dumps(RESULT)}},
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await provider.query_complete("test prompt", TestResponse)

        assert isinstance(result, TestResponse)
        assert result.value == RESULT["value"]


@pytest.mark.asyncio
async def test_query_complete_http_error(test_schema):
    """Raises APIError when HTTP request fails."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        with pytest.raises(
            APIError, match="Complete request failed: Connection failed"
        ):
            await provider.query_complete("test prompt", TestResponse)


@pytest.mark.asyncio
async def test_query_complete_invalid_json_response(test_schema):
    """Raises FormatError when response JSON is invalid."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200, json={"message": {"content": "invalid json"}}, request=mock_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(FormatError, match="Failed to parse response:"):
            await provider.query_complete("test prompt", TestResponse)


@pytest.mark.asyncio
async def test_query_complete_missing_content(test_schema):
    """Raises FormatError when response is missing required content."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        json={
            "message": {}  # Missing content field
        },
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(FormatError, match="Failed to parse response:"):
            await provider.query_complete("test prompt", TestResponse)


@pytest.mark.asyncio
async def test_query_stream_yields_chunks(test_schema):
    """Yields parsed chunks from a streaming response."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

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
        chunks = []

        async for chunk in provider.query_stream(messages, TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert chunks[0]["message"]["content"] == "chunk1"
        assert chunks[1]["message"]["content"] == "chunk2"


@pytest.mark.asyncio
async def test_query_stream_http_error(test_schema):
    """Raises APIError when streaming request fails."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Stream failed")

        with pytest.raises(APIError, match="Stream request failed: Stream failed"):
            async for _ in provider.query_stream("test prompt", TestResponse):
                pass


@pytest.mark.asyncio
async def test_query_stream_invalid_json(test_schema):
    """Raises FormatError when chunk contains invalid JSON."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

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

        with pytest.raises(FormatError, match="Failed to parse chunk:"):
            async for _ in provider.query_stream("test prompt", TestResponse):
                pass


@pytest.mark.asyncio
async def test_query_stream_empty_chunks(test_schema):
    """Skips empty chunks in the stream."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, test_schema)

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

    async def mock_aiter_lines():
        yield ""
        yield '{"message": {"content": "valid chunk"}}'
        yield ""

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []

        async for chunk in provider.query_stream("test prompt", TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "valid chunk"


@pytest.mark.asyncio
async def test_stream_history_accumulation():
    """Accumulates stream history correctly."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

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
        chunks = []

        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert len(provider.stream_history.chunks) == 2
        assert provider.stream_history.chunks[0].content == "chunk1"
        assert provider.stream_history.chunks[1].content == "chunk2"


@pytest.mark.asyncio
async def test_stream_history_parse_error():
    """Records parse errors in stream history."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, {"type": "object"})

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

        with pytest.raises(FormatError):
            async for _ in provider.query_stream([], TestResponse):
                pass

        assert len(provider.stream_history.chunks) == 1
        assert provider.stream_history.chunks[0].type == StreamChunkType.PARSE_ERROR
        assert provider.stream_history.chunks[0].error is not None


@pytest.mark.asyncio
async def test_stream_history_get_full_content():
    """Rebuilds full content from stream history."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

    async def mock_aiter_lines():
        yield '{"message": {"content": "Hello"}}'
        yield '{"message": {"content": " world"}}'
        yield '{"message": {"content": "!"}}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()

        async for _ in provider.query_stream([], TestResponse):
            pass

        assert provider.stream_history.get_full_content() == "Hello world!"


@pytest.mark.asyncio
async def test_stream_empty_line_history():
    """Records empty lines in stream history."""
    provider = OllamaProvider()
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(200, request=mock_request)

    async def mock_aiter_lines():
        yield ""
        yield '{"message": {"content": "valid chunk"}}'
        yield ""

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []

        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        # Verify chunks yielded
        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "valid chunk"

        # Verify stream history
        assert len(provider.stream_history.chunks) == 3
        assert provider.stream_history.chunks[0].type == StreamChunkType.EMPTY_LINE
        assert provider.stream_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert provider.stream_history.chunks[2].type == StreamChunkType.EMPTY_LINE
