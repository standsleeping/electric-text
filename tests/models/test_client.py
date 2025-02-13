import pytest
from dataclasses import dataclass
from unittest.mock import AsyncMock, patch
from models.client import Client


@dataclass
class MockResponse:
    event: str


@pytest.mark.asyncio
async def test_stream():
    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [
        {"message": {"content": '{"event": "one"}'}},
        {"message": {"content": '{"event": "two"}'}},
    ]

    with patch.object(client.provider, "query_stream", return_value=mock_stream):
        results = []
        async for chunk in client.stream("model", messages, MockResponse):
            results.append(chunk)

        assert len(results) == 2
        assert isinstance(results[0], MockResponse)
        assert results[0].event == "one"
        assert results[1].event == "two"


@pytest.mark.asyncio
async def test_generate():
    client = Client[MockResponse](provider_name="ollama", config={})
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]

    with patch.object(
        client.provider,
        "query_complete",
        AsyncMock(return_value=MockResponse(event="one")),
    ):
        result = await client.generate("model", messages, MockResponse)
        assert isinstance(result, MockResponse)
        assert result.event == "one"
