import pytest
import httpx
from unittest.mock import patch
from models.providers.openai import OpenaiProvider, APIError
from models.stream_history import StreamChunkType


class TestResponse:
    """Test response type for schema validation."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.mark.asyncio
async def test_stream_empty_line():
    """Skips empty lines in the stream."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")

    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield ""
        yield "data: {}"

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 0


@pytest.mark.asyncio
async def test_stream_done_marker():
    """Skips [DONE] markers in the stream."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")

    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield "data: [DONE]"
        yield 'data: {"choices":[{"delta":{"content":"test"}}]}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "test"


@pytest.mark.asyncio
async def test_stream_invalid_prefix():
    """Skips lines without data: prefix."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")

    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield "invalid: {}"
        yield 'data: {"choices":[{"delta":{"content":"test"}}]}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "test"


@pytest.mark.asyncio
async def test_stream_json_decode_error():
    """Categorizes invalid JSON as PARSE_ERROR."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

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

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 0  # No valid content chunks
        assert len(provider.stream_history.chunks) == 1
        assert provider.stream_history.chunks[0].type == StreamChunkType.PARSE_ERROR
        assert (
            provider.stream_history.chunks[0].error is not None
        )  # Just verify we have an error message


@pytest.mark.asyncio
async def test_stream_no_choices():
    """Skips chunks without choices."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")

    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield 'data: {"no_choices": true}'
        yield 'data: {"choices":[{"delta":{"content":"test"}}]}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "test"


@pytest.mark.asyncio
async def test_stream_no_content():
    """Skips chunks without content in delta."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")

    mock_response = httpx.Response(
        200,
        content=b"",
        request=mock_request,
    )

    async def mock_aiter_lines():
        yield 'data: {"choices":[{"delta":{}}]}'
        yield 'data: {"choices":[{"delta":{"content":"test"}}]}'

    mock_response.aiter_lines = mock_aiter_lines

    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_response

        async def __aexit__(self, *args):
            pass

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.return_value = AsyncContextManagerMock()
        chunks = []
        async for chunk in provider.query_stream([], TestResponse):
            chunks.append(chunk)

        assert len(chunks) == 1
        assert chunks[0]["message"]["content"] == "test"


@pytest.mark.asyncio
async def test_stream_http_error():
    """Raises APIError on HTTP errors."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(TestResponse, {"type": "object"})

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Test error")
        with pytest.raises(APIError):
            async for _ in provider.query_stream([], TestResponse):
                pass
