import pytest
from unittest.mock import AsyncMock, patch
from models.client import Client


@pytest.mark.asyncio
async def test_stream():
    client = Client(provider_name="ollama", config={})

    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = [{"event": "one"}, {"event": "two"}]

    with patch.object(client.provider, "stream", return_value=mock_stream):
        results = []
        async for chunk in client.stream("model", [], None):
            results.append(chunk)

        assert len(results) == 2
        assert results[0] == {"event": "one"}
        assert results[1] == {"event": "two"}


@pytest.mark.asyncio
async def test_generate():
    client = Client(provider_name="ollama", config={})

    with patch.object(client.provider, 'generate', AsyncMock(return_value={"event": "one"})):
        result = await client.generate("model", [], None)
        assert result == {"event": "one"}
