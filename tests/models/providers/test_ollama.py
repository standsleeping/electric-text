import json
import httpx
import pytest
from typing import Any
from unittest.mock import AsyncMock, patch

from models.providers.ollama import OllamaProvider, FormatError
from models.stream_history import StreamChunkType, StreamHistory


@pytest.fixture
def test_schema():
    """Common schema used across tests."""
    return {"type": "object", "properties": {"value": {"type": "string"}}}


class FakeResponse:
    def __init__(self, **kwargs: Any) -> None:
        self.value = kwargs.get("value")


def test_register_schema_stores_schema(test_schema):
    """A schema can be registered and stored for a response type."""
    provider = OllamaProvider()

    provider.register_schema(FakeResponse, test_schema)

    assert provider.format_schemas[FakeResponse] == test_schema


def test_register_schema_multiple_types():
    """Multiple schemas can be registered for different response types."""
    provider = OllamaProvider()
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


def test_create_payload_with_registered_schema(test_schema):
    """Creates a payload with a registered schema."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    payload = provider.create_payload(
        messages,
        FakeResponse,
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
    provider.register_schema(FakeResponse, test_schema)

    payload = provider.create_payload(
        "test prompt",
        FakeResponse,
        "custom-model",
        True,
    )

    assert payload["model"] == "custom-model"


def test_create_payload_without_schema_raises_error():
    """Creating a payload without a registered schema raises FormatError."""
    provider = OllamaProvider()

    with pytest.raises(FormatError, match="No schema registered for type FakeResponse"):
        provider.create_payload("test prompt", FakeResponse, None, False)


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
async def test_generate_completion_successful_response(test_schema):
    """Successfully parses a complete response from the API."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

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
        result = await provider.generate_completion("test prompt", FakeResponse)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
        assert result.chunks[0].content == json.dumps(RESULT)
        assert result.get_full_content() == json.dumps(RESULT)


@pytest.mark.asyncio
async def test_generate_completion_http_error(test_schema):
    """Returns StreamHistory with HTTP_ERROR chunk when HTTP request fails."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.HTTPError("Connection failed")

        result = await provider.generate_completion("test prompt", FakeResponse)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.HTTP_ERROR
        assert result.chunks[0].error == "Complete request failed: Connection failed"
        assert result.chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_completion_invalid_json_response(test_schema):
    """Records invalid JSON in stream history."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200, json={"message": {"content": "invalid json"}}, request=mock_request
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await provider.generate_completion("test prompt", FakeResponse)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.COMPLETE_RESPONSE
        assert result.chunks[0].content == "invalid json"
        assert result.get_full_content() == "invalid json"


@pytest.mark.asyncio
async def test_generate_completion_missing_content(test_schema):
    """Returns StreamHistory with FORMAT_ERROR chunk when response is missing required content."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

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

        result = await provider.generate_completion("test prompt", FakeResponse)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert "Failed to parse response" in result.chunks[0].error
        assert result.chunks[0].raw_line == '{"message":{}}'


@pytest.mark.asyncio
async def test_generate_stream_yields_chunks(test_schema):
    """Yields stream history objects containing accumulated chunks."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

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
        histories = []

        async for history in provider.generate_stream(messages, FakeResponse):
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
async def test_generate_stream_http_error(test_schema):
    """Yields StreamHistory with HTTP_ERROR chunk when streaming request fails."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Stream failed")

        histories = []
        async for history in provider.generate_stream("test prompt", FakeResponse):
            histories.append(history)

        assert len(histories) == 1
        assert isinstance(histories[0], StreamHistory)
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.HTTP_ERROR
        assert histories[0].chunks[0].error == "Stream request failed: Stream failed"
        assert histories[0].chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_stream_invalid_json(test_schema):
    """Records invalid JSON in stream history instead of raising."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

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

        async for history in provider.generate_stream("test prompt", FakeResponse):
            histories.append(history)

        # Should get one history object with the error chunk
        assert len(histories) == 1
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.PARSE_ERROR
        assert histories[0].chunks[0].raw_line == "invalid json"
        assert histories[0].chunks[0].error is not None


@pytest.mark.asyncio
async def test_generate_stream_empty_chunks(test_schema):
    """Records empty lines in stream history."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, test_schema)

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
        histories = []

        async for history in provider.generate_stream("test prompt", FakeResponse):
            histories.append(history)

        # We should get three history objects (same object, updated)
        assert len(histories) == 3
        assert histories[0] is histories[1] is histories[2]  # All same object

        # Final history should have all three chunks in order
        final_history = histories[-1]
        assert len(final_history.chunks) == 3

        # Verify chunk types and content
        assert final_history.chunks[0].type == StreamChunkType.EMPTY_LINE
        assert final_history.chunks[0].raw_line == ""

        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "valid chunk"

        assert final_history.chunks[2].type == StreamChunkType.EMPTY_LINE
        assert final_history.chunks[2].raw_line == ""

        # Verify final accumulated content
        assert final_history.get_full_content() == "valid chunk"


@pytest.mark.asyncio
async def test_stream_history_accumulation():
    """Accumulates stream history correctly."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, {"type": "object"})

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

        async for chunk in provider.generate_stream([], FakeResponse):
            chunks.append(chunk)

        assert len(chunks) == 2
        assert len(provider.stream_history.chunks) == 2
        assert provider.stream_history.chunks[0].content == "chunk1"
        assert provider.stream_history.chunks[1].content == "chunk2"


@pytest.mark.asyncio
async def test_stream_history_parse_error():
    """Records parse errors in stream history without raising."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, {"type": "object"})

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

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # Should get one history object with the error chunk
        assert len(histories) == 1
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.PARSE_ERROR
        assert histories[0].chunks[0].raw_line == "invalid json"

        # Verify error details
        assert histories[0].chunks[0].error is not None
        assert isinstance(histories[0].chunks[0].error, str)
        # The error should indicate it's a parsing error at the start of the input
        assert "line 1" in histories[0].chunks[0].error
        assert "column 1" in histories[0].chunks[0].error


@pytest.mark.asyncio
async def test_stream_history_get_full_content():
    """Rebuilds full content from stream history."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, {"type": "object"})

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

        async for _ in provider.generate_stream([], FakeResponse):
            pass

        assert provider.stream_history.get_full_content() == "Hello world!"


@pytest.mark.asyncio
async def test_stream_empty_line_history():
    """Records empty lines in stream history."""
    provider = OllamaProvider()
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get three history objects (same object, updated)
        assert len(histories) == 3
        assert histories[0] is histories[1] is histories[2]  # Identical objects

        # Final history should have all three chunks in order
        final_history = histories[-1]
        assert len(final_history.chunks) == 3

        # First chunk should be an empty line
        assert final_history.chunks[0].type == StreamChunkType.EMPTY_LINE
        assert final_history.chunks[0].raw_line == ""
        assert final_history.chunks[0].content is None

        # Second chunk should be the valid content
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "valid chunk"

        # Third chunk should be another empty line
        assert final_history.chunks[2].type == StreamChunkType.EMPTY_LINE
        assert final_history.chunks[2].raw_line == ""
        assert final_history.chunks[2].content is None

        # Verify the accumulated content only includes actual content
        assert final_history.get_full_content() == "valid chunk"
