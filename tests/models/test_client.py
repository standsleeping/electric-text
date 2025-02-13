import pytest
from dataclasses import dataclass
from unittest.mock import AsyncMock, patch
from models.client import Client, ParseResult
from models.provider import StreamHistory


@dataclass
class MockResponse:
    event: str


class MockStreamHistory(StreamHistory):
    def __init__(self, content: str):
        self._content = content

    def get_full_content(self) -> str:
        return self._content


@pytest.mark.asyncio
async def test_stream():
    """Client streams responses from the provider."""

    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        MockStreamHistory('{"event": "one"}'),
        MockStreamHistory('{"event": "two"}'),
    ]

    with patch.object(client.provider, "generate_stream", return_value=mock_stream):
        results = []
        async for result in client.stream("model", messages, MockResponse):
            results.append(result)

        assert len(results) == 2
        assert isinstance(results[0], ParseResult)
        assert results[0].is_valid
        assert results[0].model.event == "one"
        assert results[1].model.event == "two"


@pytest.mark.asyncio
async def test_stream_invalid_json():
    """Client handles invalid JSON in stream responses."""

    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [{"role": "user", "content": "Hello"}]

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        MockStreamHistory("invalid json"),
    ]

    with patch.object(client.provider, "generate_stream", return_value=mock_stream):
        results = []
        async for result in client.stream("model", messages, MockResponse):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], ParseResult)
        assert not results[0].is_valid
        assert results[0].model is None
        assert results[0].parsed_content == {}


@pytest.mark.asyncio
async def test_stream_validation_error():
    """Client handles validation errors in stream responses."""

    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [{"role": "user", "content": "Hello"}]

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        MockStreamHistory('{"wrong_field": "value"}'),
    ]

    with patch.object(client.provider, "generate_stream", return_value=mock_stream):
        results = []
        async for result in client.stream("model", messages, MockResponse):
            results.append(result)

        assert len(results) == 1
        assert isinstance(results[0], ParseResult)
        assert not results[0].is_valid
        assert results[0].parsed_content == {"wrong_field": "value"}
        assert results[0].validation_error is not None


@pytest.mark.asyncio
async def test_generate():
    """Client generates a complete response."""

    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    with patch.object(
        client.provider,
        "generate_completion",
        AsyncMock(return_value=MockResponse(event="one")),
    ):
        result = await client.generate("model", messages, MockResponse)
        assert isinstance(result, MockResponse)
        assert result.event == "one"
