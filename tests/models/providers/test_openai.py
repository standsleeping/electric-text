import pytest
import httpx
from unittest.mock import patch, AsyncMock
from models.providers.openai import OpenaiProvider, FormatError
from models.stream_history import StreamChunkType, StreamHistory


class FakeResponse:
    """Test response type for schema validation."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_create_payload_without_schema_raises_error():
    """Creating a payload without a registered schema raises FormatError."""
    provider = OpenaiProvider(api_key="test")

    with pytest.raises(FormatError, match="No schema registered for type FakeResponse"):
        provider.create_payload("test prompt", FakeResponse, None, False)


@pytest.mark.asyncio
async def test_stream_empty_line():
    """Records empty lines and data markers in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get two history objects (same object, updated)
        assert len(histories) == 2
        assert histories[0] is histories[1]  # All same object

        # Final history should have both chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 2

        # First chunk should be an empty line
        assert final_history.chunks[0].type == StreamChunkType.EMPTY_LINE
        assert final_history.chunks[0].raw_line == ""
        assert final_history.chunks[0].content is None

        # Second chunk should be a data marker with empty content
        assert final_history.chunks[1].type == StreamChunkType.NO_CHOICES
        assert final_history.chunks[1].raw_line == "data: {}"
        assert final_history.chunks[1].parsed_data == {}
        assert final_history.chunks[1].content is None

        # No actual content, so full content should be empty
        assert final_history.get_full_content() == ""


@pytest.mark.asyncio
async def test_stream_done_marker():
    """Records [DONE] markers and content in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get two history objects (same object, updated)
        assert len(histories) == 2
        assert histories[0] is histories[1]  # All same object

        # Final history should have both chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 2

        # First chunk should be a done marker
        assert final_history.chunks[0].type == StreamChunkType.STREAM_DONE
        assert final_history.chunks[0].raw_line == "data: [DONE]"
        assert final_history.chunks[0].content is None

        # Second chunk should be a content chunk
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "test"
        assert final_history.chunks[1].parsed_data == {
            "choices": [{"delta": {"content": "test"}}]
        }

        # Only content chunks contribute to accumulated content
        assert final_history.get_full_content() == "test"


@pytest.mark.asyncio
async def test_stream_invalid_prefix():
    """Records lines without data: prefix in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get two history objects (same object, updated)
        assert len(histories) == 2
        assert histories[0] is histories[1]  # All same object

        # Final history should have both chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 2

        # First chunk should be an invalid format line
        assert final_history.chunks[0].type == StreamChunkType.INVALID_FORMAT
        assert final_history.chunks[0].raw_line == "invalid: {}"
        assert final_history.chunks[0].content is None

        # Second chunk should be a content chunk
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "test"
        assert final_history.chunks[1].parsed_data == {
            "choices": [{"delta": {"content": "test"}}]
        }

        # Only content chunks contribute to accumulated content
        assert final_history.get_full_content() == "test"


@pytest.mark.asyncio
async def test_stream_json_decode_error():
    """Records JSON decode errors in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get one history object with the error chunk
        assert len(histories) == 1

        # Final history should have one chunk
        final_history = histories[-1]
        assert len(final_history.chunks) == 1

        # The chunk should be a parse error
        assert final_history.chunks[0].type == StreamChunkType.PARSE_ERROR
        assert final_history.chunks[0].raw_line == "data: invalid json"
        assert final_history.chunks[0].content is None
        assert final_history.chunks[0].parsed_data is None

        # Verify error details
        assert final_history.chunks[0].error is not None
        assert "line 1" in final_history.chunks[0].error
        assert "column 1" in final_history.chunks[0].error

        # No content chunks means empty full content
        assert final_history.get_full_content() == ""


@pytest.mark.asyncio
async def test_stream_no_choices():
    """Records chunks without choices in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get two history objects (same object, updated)
        assert len(histories) == 2
        assert histories[0] is histories[1]  # All same object

        # Final history should have both chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 2

        # First chunk should be a no-choices chunk
        assert final_history.chunks[0].type == StreamChunkType.NO_CHOICES
        assert final_history.chunks[0].raw_line == 'data: {"no_choices": true}'
        assert final_history.chunks[0].parsed_data == {"no_choices": True}
        assert final_history.chunks[0].content is None

        # Second chunk should be a content chunk
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "test"
        assert final_history.chunks[1].parsed_data == {
            "choices": [{"delta": {"content": "test"}}]
        }

        # Only content chunks contribute to accumulated content
        assert final_history.get_full_content() == "test"


@pytest.mark.asyncio
async def test_stream_no_content():
    """Records chunks without content in delta in stream history."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

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
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        # We should get two history objects (same object, updated)
        assert len(histories) == 2
        assert histories[0] is histories[1]  # All same object

        # Final history should have both chunks
        final_history = histories[-1]
        assert len(final_history.chunks) == 2

        # First chunk should be a no-choices chunk (empty delta)
        assert final_history.chunks[0].type == StreamChunkType.NO_CHOICES
        assert final_history.chunks[0].raw_line == 'data: {"choices":[{"delta":{}}]}'
        assert final_history.chunks[0].parsed_data == {"choices": [{"delta": {}}]}
        assert final_history.chunks[0].content is None

        # Second chunk should be a content chunk
        assert final_history.chunks[1].type == StreamChunkType.CONTENT_CHUNK
        assert final_history.chunks[1].content == "test"
        assert final_history.chunks[1].parsed_data == {
            "choices": [{"delta": {"content": "test"}}]
        }

        # Only content chunks contribute to accumulated content
        assert final_history.get_full_content() == "test"


@pytest.mark.asyncio
async def test_stream_http_error():
    """Yields StreamHistory with HTTP_ERROR chunk when streaming request fails."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_stream.side_effect = httpx.HTTPError("Stream failed")
        histories = []

        async for history in provider.generate_stream([], FakeResponse):
            histories.append(history)

        assert len(histories) == 1
        assert isinstance(histories[0], StreamHistory)
        assert len(histories[0].chunks) == 1
        assert histories[0].chunks[0].type == StreamChunkType.HTTP_ERROR
        assert histories[0].chunks[0].error == "Stream request failed: Stream failed"
        assert histories[0].chunks[0].raw_line == ""


@pytest.mark.asyncio
async def test_generate_completion_missing_content():
    """Returns StreamHistory with FORMAT_ERROR chunk when response is missing required content."""
    provider = OpenaiProvider(api_key="test")
    provider.register_schema(FakeResponse, {"type": "object"})

    mock_request = httpx.Request("POST", "http://test")
    mock_response = httpx.Response(
        200,
        json={
            "choices": [{"message": {}}]  # Missing content field
        },
        request=mock_request,
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "test prompt"}]
        result = await provider.generate_completion(messages, FakeResponse)

        assert isinstance(result, StreamHistory)
        assert len(result.chunks) == 1
        assert result.chunks[0].type == StreamChunkType.FORMAT_ERROR
        assert "Failed to parse response" in result.chunks[0].error
        assert result.chunks[0].raw_line == '{"choices":[{"message":{}}]}'
