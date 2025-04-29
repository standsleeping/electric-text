import httpx
import pytest
from unittest.mock import AsyncMock, patch

from electric_text.providers.model_providers.ollama import OllamaProvider
from electric_text.providers.stream_history import StreamChunkType, StreamHistory
from electric_text.responses import UserRequest


class ModelProviderError(Exception):
    """Base exception for model provider errors."""

    pass


class FormatError(ModelProviderError):
    """Error raised when response format is invalid."""

    pass


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
        json={"message": {"content": "test result"}},
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        user_request = UserRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model="llama3.1:8b"
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

        user_request = UserRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model="llama3.1:8b"
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.HTTP_ERROR
        assert result.chunks[0].error == "Complete request failed: Connection failed"
        assert result.chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_completion_missing_content():
    """Returns StreamHistory with FORMAT_ERROR chunk when response is missing required content."""
    provider = OllamaProvider()

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

        user_request = UserRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model="llama3.1:8b"
        )
        result = await provider.generate_completion(user_request)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert "Failed to parse response" in result.chunks[0].error
        assert result.chunks[0].raw_line == '{"message":{}}'


@pytest.mark.asyncio
async def test_generate_stream_yields_chunks():
    """Yields stream history objects containing accumulated chunks."""
    provider = OllamaProvider()

    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    user_request = UserRequest(
        messages=messages,
        model="llama3.1:8b"
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

        user_request = UserRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model="llama3.1:8b"
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

        user_request = UserRequest(
            messages=[{"role": "user", "content": "test prompt"}],
            model="llama3.1:8b"
        )
        async for history in provider.generate_stream(user_request):
            histories.append(history)

        # Should get one history object with the error chunk
        assert len(histories) == 1
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.PARSE_ERROR
        assert histories[0].chunks[0].raw_line == "invalid json"
        assert histories[0].chunks[0].error is not None
